"""
Handlers del bot Telegram de THDORA — v3.0 (F9.2).

Novedades F9.2:
    - Navegación ◀️▶️ en /citas y /habitos (ayer/hoy/mañana)
    - UI adaptativa según habit_config (numeric/time/boolean/text)
    - Botones rápidos desde quick_vals de HabitConfig
    - Detección de conflicto de hora al crear cita (⚠️ avisa, no bloquea)
    - Hábito repetido: opción Sobreescribir / Sumar / Cancelar
    - /config para gestionar HabitConfig desde el bot

Comandos disponibles::

    /start                → presentación y ayuda
    /citas [fecha]        → ver citas con navegación ◀️▶️
    /nueva                → crear cita (5 pasos + detección conflicto)
    /habitos [fecha]      → ver hábitos con navegación ◀️▶️
    /habito               → registrar hábito (UI adaptativa)
    /config               → gestionar configuración de hábitos
    /resumen [fecha]      → resumen completo del día
    /cancelar             → abortar operación en curso
"""

import logging
import re
from datetime import date, datetime, timedelta
from typing import Optional

try:
    import dateparser
    _HAS_DATEPARSER = True
except ImportError:
    _HAS_DATEPARSER = False

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.api_client import ApiError, ThdoraApiClient

logger = logging.getLogger(__name__)
api = ThdoraApiClient()

# ── Estados de conversación ────────────────────────────────────────────

# /nueva cita: 5 pasos + conflicto
NUEVA_DATE, NUEVA_TIME, NUEVA_NOMBRE, NUEVA_TYPE, NUEVA_NOTES, NUEVA_CONFLICT = range(6)

# /habito: 2 pasos + conflicto
HABITO_NOMBRE, HABITO_VALUE, HABITO_CONFLICT = range(10, 13)

# editar cita: 4 pasos
EDIT_APT_TIME, EDIT_APT_NOMBRE, EDIT_APT_TYPE, EDIT_APT_NOTES = range(20, 24)

# editar hábito: 1 paso
EDIT_HAB_VALUE = 30

# /config: 4 pasos
CFG_NOMBRE, CFG_TYPE, CFG_UNIT, CFG_QUICK = range(40, 44)

# ── Constantes de dominio ───────────────────────────────────────────────

TIPOS_CITA = ["médica", "personal", "trabajo", "otra"]

HABITOS_COMUNES = [
    "sueño", "THC", "tabaco", "ejercicio", "agua", "humor", "alimentacion"
]

HABIT_TYPE_EMOJIS = {
    "numeric": "🔢",
    "time":    "⏱️",
    "boolean": "✅",
    "text":    "📝",
}

_RE_TIME   = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
_RE_ACUM   = re.compile(r"^\+([\d\.]+)(.*)$")
_RE_NUMBER = re.compile(r"^([\d\.]+)(.*)$")


# ── Helpers de fecha ──────────────────────────────────────────────────────


def _parse_date_flex(text: str) -> Optional[str]:
    t = text.strip().lower()
    if t in ("hoy", "today"):         return str(date.today())
    if t in ("mañana", "manana", "tomorrow"): return str(date.today() + timedelta(days=1))
    if t in ("ayer", "yesterday"):    return str(date.today() - timedelta(days=1))
    try:
        datetime.strptime(t, "%Y-%m-%d")
        return t
    except ValueError:
        pass
    if _HAS_DATEPARSER:
        parsed = dateparser.parse(
            text, languages=["es", "en"],
            settings={"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False},
        )
        if parsed:
            return parsed.strftime("%Y-%m-%d")
    return None


def _parse_date_arg(arg: Optional[str]) -> str:
    if arg:
        result = _parse_date_flex(arg)
        if result:
            return result
    return str(date.today())


def _date_label(date_str: str) -> str:
    today = str(date.today())
    tomorrow = str(date.today() + timedelta(days=1))
    yesterday = str(date.today() - timedelta(days=1))
    if date_str == today:     return f"hoy ({date_str})"
    if date_str == tomorrow:  return f"mañana ({date_str})"
    if date_str == yesterday: return f"ayer ({date_str})"
    return date_str


def _nav_keyboard(date_str: str, prefix: str) -> InlineKeyboardMarkup:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    prev_d = str(d - timedelta(days=1))
    next_d = str(d + timedelta(days=1))
    today  = str(date.today())
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️", callback_data=f"{prefix}_nav_{prev_d}"),
        InlineKeyboardButton("📅 Hoy", callback_data=f"{prefix}_nav_{today}"),
        InlineKeyboardButton("▶️", callback_data=f"{prefix}_nav_{next_d}"),
    ]])


# ── Helper acumulación ─────────────────────────────────────────────────────


def _accumulate_value(existing: Optional[str], new_input: str) -> str:
    m_new = _RE_ACUM.match(new_input.strip())
    if not m_new:
        return new_input
    increment = float(m_new.group(1))
    unit = m_new.group(2).strip()
    if existing:
        m_old = _RE_NUMBER.match(existing.strip())
        if m_old:
            try:
                base = float(m_old.group(1))
                old_unit = m_old.group(2).strip()
                unit = unit or old_unit
                return f"{base + increment:g}{unit}"
            except ValueError:
                pass
    return f"{increment:g}{unit}"


def _clean_acum_context(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("acum_hab_date", None)
    context.user_data.pop("acum_hab_nombre", None)


# ── Helpers de formato ─────────────────────────────────────────────────────


def _fmt_appointments(apts: list, date_str: str) -> str:
    if not apts:
        return f"\ud83d\udcc5 No hay citas el *{date_str}*\\."
    lines = [f"\ud83d\udcc5 *Citas del {date_str}:*\n"]
    for a in apts:
        idx = a.get("index", "?")
        nombre = a.get("name", "") or a.get("type", "")
        notas = f"\n      _{a['notes']}_" if a.get("notes") else ""
        lines.append(f"  *{idx}\\. {a['time']}* — {nombre} \\[{a['type']}\\]{notas}")
    return "\n".join(lines)


def _fmt_habits(habits: dict, date_str: str) -> str:
    if not habits:
        return f"\ud83d\udcca No hay hábitos registrados el *{date_str}*\\."
    lines = [f"\ud83d\udcca *Hábitos del {date_str}:*\n"]
    for h, v in habits.items():
        lines.append(f"  \u2022 {h}: `{v}`")
    return "\n".join(lines)


# ── Helpers de teclados inline ───────────────────────────────────────────────


def _kb_tipos() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(t.capitalize(), callback_data=f"tipo_{t}")] for t in TIPOS_CITA]
    return InlineKeyboardMarkup(buttons)


def _kb_habitos() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(h, callback_data=f"hab_{h}")] for h in HABITOS_COMUNES]
    buttons.append([InlineKeyboardButton("\u270f\ufe0f Otro…", callback_data="hab___otro")])
    return InlineKeyboardMarkup(buttons)


def _kb_hab_value(cfg: Optional[dict]) -> Optional[InlineKeyboardMarkup]:
    if not cfg:
        return None
    habit_type = cfg.get("habit_type", "text")
    quick_vals = cfg.get("quick_vals", [])

    if habit_type == "boolean":
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("\u2705 Sí", callback_data="hval_1"),
            InlineKeyboardButton("\u274c No",  callback_data="hval_0"),
        ]])

    if quick_vals:
        row, rows = [], []
        for val in quick_vals:
            row.append(InlineKeyboardButton(val, callback_data=f"hval_{val}"))
            if len(row) == 3:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        rows.append([InlineKeyboardButton("\u270f\ufe0f Otro valor", callback_data="hval___otro")])
        return InlineKeyboardMarkup(rows)

    return None


def _kb_apt_actions(date_str: str, index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\ud83d\uddd1\ufe0f Borrar", callback_data=f"ad_{date_str}_{index}"),
        InlineKeyboardButton("\u270f\ufe0f Editar",  callback_data=f"ae_{date_str}_{index}"),
    ]])


def _kb_apt_confirm(date_str: str, index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\u2705 Sí, borrar", callback_data=f"adc_{date_str}_{index}"),
        InlineKeyboardButton("\u274c Cancelar",   callback_data="cancel_action"),
    ]])


def _kb_hab_actions(date_str: str, habit: str) -> InlineKeyboardMarkup:
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\ud83d\uddd1\ufe0f", callback_data=f"hd_{date_str}_{h}"),
        InlineKeyboardButton("\u270f\ufe0f",       callback_data=f"he_{date_str}_{h}"),
        InlineKeyboardButton("\u2795",             callback_data=f"ha_{date_str}_{h}"),
    ]])


def _kb_hab_confirm(date_str: str, habit: str) -> InlineKeyboardMarkup:
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\u2705 Sí, borrar", callback_data=f"hdc_{date_str}_{h}"),
        InlineKeyboardButton("\u274c Cancelar",   callback_data="cancel_action"),
    ]])


def _kb_hab_conflict(nombre: str, existing_val: str, new_val: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\u270f\ufe0f Sobreescribir", callback_data="hconf_overwrite"),
        InlineKeyboardButton("\u2795 Sumar",               callback_data="hconf_add"),
        InlineKeyboardButton("\u274c Cancelar",            callback_data="hconf_cancel"),
    ]])


def _kb_conflict_apt(date_str: str, time: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("\u2705 Crear de todas formas", callback_data="aptconf_ok"),
        InlineKeyboardButton("\u274c Cambiar hora",          callback_data="aptconf_change"),
    ]])


# ── /start ───────────────────────────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "\ud83d\udc4b *Hola, soy THDORA*\n"
        "_Tu asistente personal de gestión de vida_\n\n"
        "*Citas:*\n"
        "  \ud83d\udcc5 /citas `[fecha]` \u2014 ver citas del día\n"
        "  \u2795 /nueva \u2014 crear una cita\n\n"
        "*Hábitos:*\n"
        "  \ud83d\udcca /habitos `[fecha]` \u2014 ver hábitos\n"
        "  \u270f\ufe0f /habito \u2014 registrar un hábito\n"
        "  \u2699\ufe0f /config \u2014 configurar tipos de hábitos\n\n"
        "*Resumen:*\n"
        "  \ud83d\udccb /resumen `[fecha]` \u2014 resumen completo del día\n\n"
        "*Fechas:* `hoy`, `mañana`, `ayer`, `27/03`, `2026-03-27`\n\n"
        "\u274c /cancelar \u2014 abortar operación en curso"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ── /citas con navegación ◀️▶️ ─────────────────────────────────────────────────


async def cmd_citas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clean_acum_context(context)
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_citas(update.message, date_str)


async def _show_citas(msg, date_str: str) -> None:
    try:
        apts = await api.get_appointments(date_str)
    except ApiError:
        await msg.reply_text("\u26a0\ufe0f Error al conectar con la API\.")
        return

    label = _date_label(date_str)
    nav = _nav_keyboard(date_str, "citas")

    if not apts:
        await msg.reply_text(
            f"\ud83d\udcc5 No hay citas el *{label}*\\.",
            parse_mode="Markdown",
            reply_markup=nav,
        )
        return

    await msg.reply_text(f"\ud83d\udcc5 *Citas del {label}:*", parse_mode="Markdown", reply_markup=nav)
    for apt in apts:
        idx = apt.get("index", 0)
        nombre = apt.get("name", "") or apt.get("type", "")
        notas = f"\n\ud83d\udcdd _{apt['notes']}_" if apt.get("notes") else ""
        text = f"\ud83d\udcc5 *{apt['time']}* \u2014 {nombre} \\[{apt['type']}\\]{notas}"
        await msg.reply_text(
            text, parse_mode="Markdown",
            reply_markup=_kb_apt_actions(date_str, idx),
        )


async def cb_citas_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str = query.data.replace("citas_nav_", "")
    await _show_citas(query.message, date_str)


# ── /habitos con navegación ◀️▶️ ────────────────────────────────────────────────


async def cmd_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clean_acum_context(context)
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_habitos(update.message, date_str)


async def _show_habitos(msg, date_str: str) -> None:
    try:
        habits = await api.get_habits(date_str)
    except ApiError:
        await msg.reply_text("\u26a0\ufe0f Error al conectar con la API\.")
        return

    label = _date_label(date_str)
    nav = _nav_keyboard(date_str, "habitos")

    if not habits:
        await msg.reply_text(
            f"\ud83d\udcca No hay hábitos el *{label}*\\.",
            parse_mode="Markdown",
            reply_markup=nav,
        )
        return

    await msg.reply_text(f"\ud83d\udcca *Hábitos del {label}:*", parse_mode="Markdown", reply_markup=nav)
    for h, v in habits.items():
        await msg.reply_text(
            f"\u2022 *{h}*: `{v}`",
            parse_mode="Markdown",
            reply_markup=_kb_hab_actions(date_str, h),
        )


async def cb_habitos_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str = query.data.replace("habitos_nav_", "")
    await _show_habitos(query.message, date_str)


# ── Callbacks de citas (borrar/editar) ────────────────────────────────────────────


async def cb_apt_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    await query.edit_message_reply_markup(reply_markup=_kb_apt_confirm(date_str, int(idx_str)))


async def cb_apt_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    try:
        ok = await api.delete_appointment(date_str, int(idx_str))
        msg = "\ud83d\uddd1\ufe0f Cita eliminada\\." if ok else "\u26a0\ufe0f Cita no encontrada \\(ya fue borrada\\)\\."
        await query.edit_message_text(msg, parse_mode="Markdown")
    except ApiError:
        await query.edit_message_text("\u26a0\ufe0f Error al borrar la cita\\.", parse_mode="Markdown")


async def cb_apt_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    context.user_data["edit_apt_date"] = date_str
    context.user_data["edit_apt_index"] = int(idx_str)
    await query.edit_message_text(
        f"\u270f\ufe0f *Editar cita {idx_str} del {date_str}*\n\nNueva hora \\(HH:MM\\) o /skip:",
        parse_mode="Markdown",
    )
    return EDIT_APT_TIME


async def cb_apt_edit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() != "/skip":
        if not _RE_TIME.match(text):
            await update.message.reply_text("\u274c Formato incorrecto\\. Usa `HH:MM` o /skip\\.", parse_mode="Markdown")
            return EDIT_APT_TIME
        context.user_data["edit_apt_time"] = text
    await update.message.reply_text("Nuevo nombre o /skip:")
    return EDIT_APT_NOMBRE


async def cb_apt_edit_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() != "/skip":
        context.user_data["edit_apt_nombre"] = text
    await update.message.reply_text(
        "Nuevo tipo o /skip:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(t.capitalize(), callback_data=f"etipo_{t}") for t in TIPOS_CITA]]
            + [[InlineKeyboardButton("\u23ed\ufe0f Skip", callback_data="etipo_skip")]]
        )
    )
    return EDIT_APT_TYPE


async def cb_apt_edit_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("etipo_", "")
    if value != "skip":
        context.user_data["edit_apt_type"] = value
    await query.edit_message_text("Nuevas notas o /skip:")
    return EDIT_APT_NOTES


async def cb_apt_edit_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    notes = text if text.lower() != "/skip" else None
    date_str = context.user_data.get("edit_apt_date", "")
    index   = context.user_data.get("edit_apt_index", 0)
    try:
        await api.update_appointment(
            date_str, index,
            time=context.user_data.get("edit_apt_time"),
            name=context.user_data.get("edit_apt_nombre"),
            apt_type=context.user_data.get("edit_apt_type"),
            notes=notes,
        )
        await update.message.reply_text(f"\u2705 *Cita {index} actualizada\\.*", parse_mode="Markdown")
    except ApiError:
        await _reply_api_error(update)
    context.user_data.clear()
    return ConversationHandler.END


# ── /nueva — ConversationHandler (5 pasos + conflicto hora) ─────────────────────


async def nueva_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "\ud83d\udcc5 *Nueva cita \u2014 paso 1/5*\n\n\u00bfPara qué fecha?\n`hoy`, `mañana`, `27/03`\u2026",
        parse_mode="Markdown",
    )
    return NUEVA_DATE


async def nueva_recv_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_str = _parse_date_flex(update.message.text.strip())
    if not date_str:
        await update.message.reply_text("\u274c No entendí la fecha\\. Prueba con `hoy`, `mañana` o `2026-03-27`\\.", parse_mode="Markdown")
        return NUEVA_DATE
    context.user_data["nueva_date"] = date_str
    await update.message.reply_text(
        f"\u2705 Fecha: *{date_str}*\n\n\ud83d\udd70 *Paso 2/5* \u2014 \u00bfA qué hora? \\(formato `HH:MM`, 24h\\)",
        parse_mode="Markdown",
    )
    return NUEVA_TIME


async def nueva_recv_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not _RE_TIME.match(text):
        await update.message.reply_text("\u274c Formato incorrecto\\. Usa `HH:MM` \\(ej: `10:30`\\)\\.", parse_mode="Markdown")
        return NUEVA_TIME

    context.user_data["nueva_time"] = text
    date_str = context.user_data.get("nueva_date", str(date.today()))

    try:
        conflict = await api.check_appointment_conflict(date_str, text)
        if conflict:
            nombre_conflict = conflict.get("name") or conflict.get("type", "cita")
            await update.message.reply_text(
                f"\u26a0\ufe0f *Ya tienes una cita a las {text}:* _{nombre_conflict}_\n\n"
                "\u00bfQuieres crear esta cita de todas formas o cambiar la hora?",
                parse_mode="Markdown",
                reply_markup=_kb_conflict_apt(date_str, text),
            )
            return NUEVA_CONFLICT
    except (ApiError, Exception):
        pass

    await update.message.reply_text(
        f"\u2705 Hora: *{text}*\n\n\ud83d\udcdd *Paso 3/5* \u2014 \u00bfCómo se llama la cita?",
        parse_mode="Markdown",
    )
    return NUEVA_NOMBRE


async def nueva_conflict_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "aptconf_ok":
        time = context.user_data.get("nueva_time", "")
        await query.edit_message_text(
            f"\u2705 Hora: *{time}*\n\n\ud83d\udcdd *Paso 3/5* \u2014 \u00bfCómo se llama la cita?",
            parse_mode="Markdown",
        )
        return NUEVA_NOMBRE
    else:
        await query.edit_message_text(
            "\ud83d\udd70 Escribe la nueva hora \\(HH:MM\\):",
            parse_mode="Markdown",
        )
        return NUEVA_TIME


async def nueva_recv_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("\u274c El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return NUEVA_NOMBRE
    context.user_data["nueva_nombre"] = nombre
    await update.message.reply_text(
        f"\u2705 Nombre: *{nombre}*\n\n\ud83d\udccb *Paso 4/5* \u2014 \u00bfTipo de cita?",
        parse_mode="Markdown",
        reply_markup=_kb_tipos(),
    )
    return NUEVA_TYPE


async def nueva_recv_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    apt_type = query.data.replace("tipo_", "")
    context.user_data["nueva_type"] = apt_type
    await query.edit_message_text(
        f"\u2705 Tipo: *{apt_type}*\n\n\ud83d\udcdd *Paso 5/5* \u2014 \u00bfAlguna nota? \\(/skip para omitir\\)",
        parse_mode="Markdown",
    )
    return NUEVA_NOTES


async def nueva_recv_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _save_appointment(update, context, update.message.text.strip())

async def nueva_skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _save_appointment(update, context, "")


async def _save_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE, notes: str) -> int:
    d  = context.user_data.get("nueva_date", str(date.today()))
    t  = context.user_data.get("nueva_time", "")
    nm = context.user_data.get("nueva_nombre", "")
    tp = context.user_data.get("nueva_type", "otra")
    try:
        result = await api.create_appointment(d, t, nm, tp, notes)
        idx = result.get("index", "?")
        notes_str = notes or "—"
        await update.message.reply_text(
            f"\u2705 *Cita creada*\n\n"
            f"  \ud83d\udcc5 {d}  \ud83d\udd70 {t}\n"
            f"  \ud83d\udcdd {nm}\n"
            f"  \ud83d\udccb {tp}\n"
            f"  \ud83d\udcac {notes_str}\n"
            f"  idx: {idx}",
            parse_mode="Markdown",
        )
    except ApiError:
        await _reply_api_error(update)
    context.user_data.clear()
    return ConversationHandler.END


# ── Callbacks de hábitos (borrar/editar/sumar) ────────────────────────────────────


async def cb_hab_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    await query.edit_message_reply_markup(reply_markup=_kb_hab_confirm(date_str, habit))


async def cb_hab_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    try:
        ok = await api.delete_habit(date_str, habit)
        msg = "\ud83d\uddd1\ufe0f Hábito eliminado\\." if ok else "\u26a0\ufe0f Hábito no encontrado \\(ya fue borrado\\)\\."
        await query.edit_message_text(msg, parse_mode="Markdown")
    except ApiError:
        await query.edit_message_text("\u26a0\ufe0f Error al borrar el hábito\\.", parse_mode="Markdown")


async def cb_hab_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    context.user_data["edit_hab_date"]   = date_str
    context.user_data["edit_hab_nombre"] = habit

    try:
        cfg = await api.get_habit_config(habit)
    except Exception:
        cfg = None

    kb = _kb_hab_value(cfg)
    hint = ""
    if cfg:
        htype = cfg.get("habit_type", "text")
        unit  = cfg.get("unit") or ""
        hint  = f" \\({HABIT_TYPE_EMOJIS.get(htype, '')} {htype}{' · ' + unit if unit else ''}\\)"

    await query.edit_message_text(
        f"\u270f\ufe0f *Editar hábito '{habit}'*{hint}\n\nNuevo valor:",
        parse_mode="Markdown",
        reply_markup=kb,
    )
    return EDIT_HAB_VALUE


async def cb_hab_edit_value_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("hval_", "")
    if value == "__otro":
        await query.edit_message_text("\u270f\ufe0f Escribe el nuevo valor:")
        return EDIT_HAB_VALUE
    return await _do_edit_habit(query.message, context, value, is_edit=True)


async def cb_hab_edit_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _do_edit_habit(update.message, context, update.message.text.strip(), is_edit=True)


async def _do_edit_habit(msg, context, value: str, is_edit: bool) -> int:
    date_str = context.user_data.get("edit_hab_date", "")
    habit    = context.user_data.get("edit_hab_nombre", "")
    try:
        await api.update_habit(date_str, habit, value)
        await msg.reply_text(f"\u2705 *{habit}* actualizado a `{value}`\\.", parse_mode="Markdown")
    except ApiError:
        await msg.reply_text("\u26a0\ufe0f Error al actualizar el hábito\.")
    context.user_data.clear()
    return ConversationHandler.END


async def cb_hab_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    context.user_data["acum_hab_date"]   = date_str
    context.user_data["acum_hab_nombre"] = habit
    await query.edit_message_text(
        f"\u2795 *Sumar a '{habit}'*\n\n"
        "Escribe el incremento \\(ej: `\\+2`, `\\+30min`, `\\+1\.5L`\\)\n"
        "O escribe el nuevo valor directo para sobreescribir:",
        parse_mode="Markdown",
    )


async def cb_hab_add_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_input = update.message.text.strip()
    date_str  = context.user_data.get("acum_hab_date", "")
    habit     = context.user_data.get("acum_hab_nombre", "")
    if not date_str or not habit:
        return
    try:
        habits = await api.get_habits(date_str)
        existing = habits.get(habit)
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, habit, final_value)
        op = "acumulado" if new_input.startswith("+") else "actualizado"
        await update.message.reply_text(
            f"\u2705 *{habit}* {op}: `{existing or '0'}` \u2192 `{final_value}`",
            parse_mode="Markdown",
        )
    except ApiError:
        await _reply_api_error(update)
    _clean_acum_context(context)


# ── /habito — ConversationHandler con UI adaptativa ───────────────────────────


async def habito_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["habito_date"] = str(date.today())
    await update.message.reply_text(
        "\u270f\ufe0f *Registrar hábito \u2014 paso 1/2*\n\n\u00bfQué hábito registras hoy?",
        parse_mode="Markdown",
        reply_markup=_kb_habitos(),
    )
    return HABITO_NOMBRE


async def habito_recv_nombre_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    nombre = query.data.replace("hab_", "")
    if nombre == "__otro":
        await query.edit_message_text("\u270f\ufe0f Escribe el nombre del hábito:")
        return HABITO_NOMBRE
    context.user_data["habito_nombre"] = nombre
    return await _ask_habito_value(query.message, context, nombre, edit=True)


async def habito_recv_nombre_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("\u274c El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return HABITO_NOMBRE
    context.user_data["habito_nombre"] = nombre
    return await _ask_habito_value(update.message, context, nombre, edit=False)


async def _ask_habito_value(msg, context, nombre: str, edit: bool) -> int:
    try:
        cfg = await api.get_habit_config(nombre)
    except Exception:
        cfg = None

    kb = _kb_hab_value(cfg)
    hint = ""
    if cfg:
        htype = cfg.get("habit_type", "text")
        unit  = cfg.get("unit") or ""
        hint  = f" \\({HABIT_TYPE_EMOJIS.get(htype, '')} {htype}{' · ' + unit if unit else ''}\\)"

    prompt = (
        f"\u2705 Hábito: *{nombre}*{hint}\n\n"
        "\ud83d\udcca *Paso 2/2* \u2014 \u00bfCuál es el valor?"
    )
    if kb:
        await msg.reply_text(prompt, parse_mode="Markdown", reply_markup=kb)
    else:
        await msg.reply_text(
            prompt + " \\(ej: `8h`, `30min`, `2L`, texto libre\\)\n"
            "Usa `\\+N` para acumular\\.",
            parse_mode="Markdown",
        )
    return HABITO_VALUE


async def habito_recv_value_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("hval_", "")
    if value == "__otro":
        await query.edit_message_text("\u270f\ufe0f Escribe el valor:")
        return HABITO_VALUE
    return await _save_habito(query.message, context, value)


async def habito_recv_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    if not value:
        await update.message.reply_text("\u274c El valor no puede estar vacío\\.", parse_mode="Markdown")
        return HABITO_VALUE
    return await _save_habito(update.message, context, value)


async def _save_habito(msg, context, new_input: str) -> int:
    nombre   = context.user_data.get("habito_nombre", "")
    date_str = context.user_data.get("habito_date", str(date.today()))
    try:
        habits   = await api.get_habits(date_str)
        existing = habits.get(nombre)

        if existing and not new_input.startswith("+"):
            context.user_data["habito_new_val"]      = new_input
            context.user_data["habito_existing_val"] = existing
            await msg.reply_text(
                f"\u26a0\ufe0f *{nombre}* ya tiene valor `{existing}` hoy\.\n"
                f"\u00bfQué quieres hacer con el nuevo valor `{new_input}`?",
                parse_mode="Markdown",
                reply_markup=_kb_hab_conflict(nombre, existing, new_input),
            )
            return HABITO_CONFLICT

        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, nombre, final_value)
        extra = f"\n  ({existing} + {new_input[1:]} = {final_value})" if new_input.startswith("+") and existing else ""
        await msg.reply_text(
            f"\u2705 *Hábito registrado*\n\n"
            f"  \ud83d\udcca {nombre}: `{final_value}`\n"
            f"  \ud83d\udcc5 {date_str}{extra}",
            parse_mode="Markdown",
        )
    except ApiError:
        await _reply_api_error_msg(msg)
    context.user_data.clear()
    return ConversationHandler.END


async def habito_conflict_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    nombre      = context.user_data.get("habito_nombre", "")
    date_str    = context.user_data.get("habito_date", str(date.today()))
    new_val     = context.user_data.get("habito_new_val", "")
    existing    = context.user_data.get("habito_existing_val", "")

    if query.data == "hconf_cancel":
        await query.edit_message_text("\u274c Operación cancelada\\.")
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "hconf_add":
        final_value = _accumulate_value(existing, f"+{new_val}")
    else:
        final_value = new_val

    try:
        await api.log_habit(date_str, nombre, final_value)
        op = "sumado" if query.data == "hconf_add" else "sobreescrito"
        await query.edit_message_text(
            f"\u2705 *{nombre}* {op}: `{existing}` \u2192 `{final_value}`",
            parse_mode="Markdown",
        )
    except ApiError:
        await query.edit_message_text("\u26a0\ufe0f Error al guardar el hábito\.")

    context.user_data.clear()
    return ConversationHandler.END


# ── /config — gestionar HabitConfig ───────────────────────────────────────────────


async def cmd_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        configs = await api.get_all_habit_configs()
    except Exception:
        configs = []

    if configs:
        lines = ["\u2699\ufe0f *Configuración de hábitos:*\n"]
        for c in configs:
            emoji = HABIT_TYPE_EMOJIS.get(c["habit_type"], "\ud83d\udcdd")
            unit  = f" ({c['unit']})" if c.get("unit") else ""
            quick = ", ".join(c["quick_vals"]) if c.get("quick_vals") else "texto libre"
            xp    = f" | XP: {c['xp_rule']}" if c.get("xp_rule") else ""
            lines.append(f"  {emoji} *{c['name']}*{unit} \u2014 {c['habit_type']}{xp}\n     Botones: {quick}")
        text = "\n".join(lines)
    else:
        text = "\u2699\ufe0f No hay ningún hábito configurado todavía\."

    await update.message.reply_text(
        text + "\n\n\u2795 Escribe el nombre del hábito que quieres configurar:",
        parse_mode="Markdown",
    )
    return CFG_NOMBRE


async def cfg_recv_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("\u274c El nombre no puede estar vacío\.")
        return CFG_NOMBRE
    context.user_data["cfg_nombre"] = nombre
    await update.message.reply_text(
        f"\u2699\ufe0f Configurando: *{nombre}*\n\n\u00bfQué tipo de hábito es?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("\ud83d\udd22 Numérico",  callback_data="cfgt_numeric"),
            InlineKeyboardButton("\u23f1\ufe0f Tiempo",    callback_data="cfgt_time"),
        ], [
            InlineKeyboardButton("\u2705 Sí/No",       callback_data="cfgt_boolean"),
            InlineKeyboardButton("\ud83d\udcdd Texto",      callback_data="cfgt_text"),
        ]])
    )
    return CFG_TYPE


async def cfg_recv_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    habit_type = query.data.replace("cfgt_", "")
    context.user_data["cfg_type"] = habit_type

    if habit_type == "boolean":
        await _save_habit_config(query.message, context, unit=None, quick_vals=None)
        return ConversationHandler.END

    await query.edit_message_text(
        f"\u2705 Tipo: *{habit_type}*\n\n\u00bfCuál es la unidad? \\(ej: `h`, `min`, `L`, `veces`\\)\n"
        "O /skip si no tiene unidad:",
        parse_mode="Markdown",
    )
    return CFG_UNIT


async def cfg_recv_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    unit = None if text.lower() == "/skip" else text
    context.user_data["cfg_unit"] = unit
    await update.message.reply_text(
        "\ud83d\ude80 Botones rápidos: escribe los valores separados por comas\n"
        "Ej: `6h,7h,8h,9h` o `1,2,3,4,5,6,7,8,9,10`\n"
        "O /skip para no tener botones rápidos:"
    )
    return CFG_QUICK


async def cfg_recv_quick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    quick_vals = None
    if text.lower() != "/skip" and text:
        quick_vals = [v.strip() for v in text.split(",") if v.strip()]
    await _save_habit_config(update.message, context, context.user_data.get("cfg_unit"), quick_vals)
    return ConversationHandler.END


async def _save_habit_config(msg, context, unit, quick_vals) -> None:
    nombre     = context.user_data.get("cfg_nombre", "")
    habit_type = context.user_data.get("cfg_type", "text")
    try:
        await api.upsert_habit_config(
            name=nombre, habit_type=habit_type,
            unit=unit, quick_vals=quick_vals,
        )
        quick_str = ", ".join(quick_vals) if quick_vals else "texto libre"
        await msg.reply_text(
            f"\u2705 *{nombre}* configurado:\n"
            f"  Tipo: {habit_type}  Unidad: {unit or '\u2014'}\n"
            f"  Botones: {quick_str}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await msg.reply_text(f"\u26a0\ufe0f Error al guardar la config: {e}")
    context.user_data.clear()


# ── /resumen ───────────────────────────────────────────────────────────────


async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        summary = await api.get_summary(date_str)
        apts    = summary.get("appointments", [])
        habits  = summary.get("habits", {})
        text = (
            f"\ud83d\udccb *Resumen del {date_str}*\n\n"
            + _fmt_appointments(apts, date_str)
            + "\n\n"
            + _fmt_habits(habits, date_str)
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except ApiError:
        await _reply_api_error(update)


# ── /cancelar ───────────────────────────────────────────────────────────────


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("\u274c Operación cancelada\\.", parse_mode="Markdown")
    return ConversationHandler.END


async def cb_cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("Cancelado")
    await query.delete_message()


# ── Error handler ─────────────────────────────────────────────────────────────


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Error no controlado en update %s: %s", update, context.error, exc_info=True)


async def _reply_api_error(update: Update) -> None:
    msg = update.message or (update.callback_query.message if update.callback_query else None)
    if msg:
        await msg.reply_text(
            "\u26a0\ufe0f No pude conectar con la API de THDORA\.\n"
            "Asegúrate de que está corriendo:\n"
            "```\nmake run-api\n```",
            parse_mode="Markdown",
        )


async def _reply_api_error_msg(msg) -> None:
    await msg.reply_text(
        "\u26a0\ufe0f No pude conectar con la API de THDORA\.\n"
        "Asegúrate de que está corriendo: `make run-api`",
        parse_mode="Markdown",
    )


# ── Factories de ConversationHandler ─────────────────────────────────────────────────


def build_nueva_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("nueva", nueva_start)],
        states={
            NUEVA_DATE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_date)],
            NUEVA_TIME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_time)],
            NUEVA_CONFLICT: [CallbackQueryHandler(nueva_conflict_response, pattern=r"^aptconf_")],
            NUEVA_NOMBRE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_nombre)],
            NUEVA_TYPE:     [CallbackQueryHandler(nueva_recv_type, pattern=r"^tipo_")],
            NUEVA_NOTES:    [
                CommandHandler("skip", nueva_skip_notes),
                MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_notes),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="nueva_cita", persistent=False, per_message=False,
    )


def build_habito_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("habito", habito_start)],
        states={
            HABITO_NOMBRE: [
                CallbackQueryHandler(habito_recv_nombre_inline, pattern=r"^hab_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_nombre_text),
            ],
            HABITO_VALUE: [
                CallbackQueryHandler(habito_recv_value_inline, pattern=r"^hval_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_value_text),
            ],
            HABITO_CONFLICT: [
                CallbackQueryHandler(habito_conflict_response, pattern=r"^hconf_"),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="registrar_habito", persistent=False, per_message=False,
    )


def build_edit_apt_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_apt_edit_start, pattern=r"^ae_")],
        states={
            EDIT_APT_TIME:   [
                CommandHandler("skip", lambda u, c: _skip_to(u, c, EDIT_APT_NOMBRE, "Nuevo nombre o /skip:")),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_time),
            ],
            EDIT_APT_NOMBRE: [
                CommandHandler("skip", _skip_to_type),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_nombre),
            ],
            EDIT_APT_TYPE:  [CallbackQueryHandler(cb_apt_edit_type, pattern=r"^etipo_")],
            EDIT_APT_NOTES: [
                CommandHandler("skip", lambda u, c: cb_apt_edit_notes(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_notes),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="editar_cita", persistent=False, per_message=False,
    )


def build_edit_hab_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_hab_edit_start, pattern=r"^he_")],
        states={
            EDIT_HAB_VALUE: [
                CallbackQueryHandler(cb_hab_edit_value_inline, pattern=r"^hval_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_hab_edit_value_text),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="editar_habito", persistent=False, per_message=False,
    )


def build_config_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("config", cmd_config)],
        states={
            CFG_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_nombre)],
            CFG_TYPE:   [CallbackQueryHandler(cfg_recv_type, pattern=r"^cfgt_")],
            CFG_UNIT:   [
                CommandHandler("skip", lambda u, c: cfg_recv_unit(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_unit),
            ],
            CFG_QUICK:  [
                CommandHandler("skip", lambda u, c: cfg_recv_quick(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_quick),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="config_habito", persistent=False, per_message=False,
    )


# ── Helpers skip internos ─────────────────────────────────────────────────────


async def _skip_to(update: Update, context: ContextTypes.DEFAULT_TYPE, next_state: int, prompt: str) -> int:
    await update.message.reply_text(prompt)
    return next_state


async def _skip_to_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Nuevo tipo o /skip:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(t.capitalize(), callback_data=f"etipo_{t}") for t in TIPOS_CITA]]
            + [[InlineKeyboardButton("\u23ed\ufe0f Skip", callback_data="etipo_skip")]]
        )
    )
    return EDIT_APT_TYPE
