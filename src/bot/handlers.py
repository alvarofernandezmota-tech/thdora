"""
Handlers del bot Telegram de THDORA — v3.4 (F9.5-c2)

Cambios sobre v3.3:
    - Eliminar HABITOS_COMUNES hardcodeados — el usuario escribe el nombre libremente
    - ➕ Nuevo hábito directo desde vista hábitos del día (quick_habito_DATE)
    - Flujo /habito: fecha prefijada → nombre libre → valor (igual que /nueva)
    - ✏️ Editar hábito: ahora permite cambiar también el NOMBRE (nuevo estado EDIT_HAB_NOMBRE)
    - Mismo patrón visual que citas: pasos numerados, confirmación final con resumen
    - Si el hábito tiene /config → botones rápidos de valor; si no → campo libre
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
NUEVA_DATE, NUEVA_TIME, NUEVA_NOMBRE, NUEVA_TYPE, NUEVA_NOTES, NUEVA_CONFLICT = range(6)
HABITO_NOMBRE, HABITO_VALUE, HABITO_CONFLICT = range(10, 13)
EDIT_APT_TIME, EDIT_APT_NOMBRE, EDIT_APT_TYPE, EDIT_APT_NOTES = range(20, 24)
EDIT_HAB_NOMBRE, EDIT_HAB_VALUE = range(30, 32)   # C2: añadido EDIT_HAB_NOMBRE
CFG_NOMBRE, CFG_TYPE, CFG_UNIT, CFG_QUICK = range(40, 44)

# ── Constantes ────────────────────────────────────────────────────────
TIPOS_CITA = ["médica", "personal", "trabajo", "otra"]
HABIT_TYPE_EMOJIS = {"numeric": "🔢", "time": "⏱️", "boolean": "✅", "text": "📝"}
_RE_TIME   = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
_RE_ACUM   = re.compile(r"^\+([\d\.]+)(.*)$")
_RE_NUMBER = re.compile(r"^([\d\.]+)(.*)$")


# ════════════════════════════════════════════════════════════════════════
# HELPERS DE FECHA
# ════════════════════════════════════════════════════════════════════════

def _parse_date_flex(text: str) -> Optional[str]:
    t = text.strip().lower()
    if t in ("hoy", "today"):                     return str(date.today())
    if t in ("mañana", "manana", "tomorrow"):     return str(date.today() + timedelta(days=1))
    if t in ("ayer", "yesterday"):                return str(date.today() - timedelta(days=1))
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
        r = _parse_date_flex(arg)
        if r: return r
    return str(date.today())


def _date_label(date_str: str) -> str:
    today     = str(date.today())
    tomorrow  = str(date.today() + timedelta(days=1))
    yesterday = str(date.today() - timedelta(days=1))
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    dow = day_names[d.weekday()]
    months = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
    short = f"{dow} {d.day} {months[d.month-1]}"
    if date_str == today:     return f"hoy — {short}"
    if date_str == tomorrow:  return f"mañana — {short}"
    if date_str == yesterday: return f"ayer — {short}"
    return short


def _date_short(date_str: str) -> str:
    """Etiqueta corta para el botón central de navegación: 'Sáb 28 mar'."""
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    months    = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
    return f"{day_names[d.weekday()]} {d.day} {months[d.month-1]}"


def _greeting() -> str:
    """Saludo contextual según hora del día."""
    hour = datetime.now().hour
    if 6 <= hour < 14:  return "🌅 Buenos días"
    if 14 <= hour < 22: return "🌆 Buenas tardes"
    return "🌙 Buenas noches"


# ════════════════════════════════════════════════════════════════════════
# HELPERS DE ACUMULACIÓN
# ════════════════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════════════════
# HELPERS DE FORMATO
# ════════════════════════════════════════════════════════════════════════

def _fmt_appointments(apts: list, date_str: str) -> str:
    if not apts:
        return f"📅 No hay citas el *{date_str}*\\."
    lines = [f"📅 *Citas del {date_str}:*\n"]
    for a in apts:
        idx    = a.get("index", "?")
        nombre = a.get("name", "") or a.get("type", "")
        notas  = f"\n      _{a['notes']}_" if a.get("notes") else ""
        lines.append(f"  *{idx}\\. {a['time']}* — {nombre} \\[{a['type']}\\]{notas}")
    return "\n".join(lines)


def _fmt_habits(habits: dict, date_str: str) -> str:
    if not habits:
        return f"📊 No hay hábitos registrados el *{date_str}*\\."
    lines = [f"📊 *Hábitos del {date_str}:*\n"]
    for h, v in habits.items():
        lines.append(f"  • {h}: `{v}`")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════
# TECLADOS
# ════════════════════════════════════════════════════════════════════════

def _nav_keyboard(date_str: str, prefix: str) -> InlineKeyboardMarkup:
    """Barra de navegación ◀️ [Fecha real] ▶️ + cambio de vista + 🏠 Menú."""
    d      = datetime.strptime(date_str, "%Y-%m-%d").date()
    prev_d = str(d - timedelta(days=1))
    next_d = str(d + timedelta(days=1))
    center_label = _date_short(date_str)
    other  = "habitos" if prefix == "citas" else "citas"
    other_emoji = "📊" if prefix == "citas" else "📅"
    if prefix == "citas":
        quick_btn = InlineKeyboardButton("➕ Nueva", callback_data=f"quick_nueva_{date_str}")
    else:
        quick_btn = InlineKeyboardButton("➕ Nuevo", callback_data=f"quick_habito_{date_str}")
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️",           callback_data=f"{prefix}_nav_{prev_d}"),
            InlineKeyboardButton(center_label,   callback_data=f"{prefix}_nav_{date_str}"),
            InlineKeyboardButton("▶️",           callback_data=f"{prefix}_nav_{next_d}"),
        ],
        [
            quick_btn,
            InlineKeyboardButton(f"{other_emoji} {other.capitalize()}", callback_data=f"{other}_nav_{date_str}"),
        ],
        [
            InlineKeyboardButton("📋 Semana", callback_data=f"semana_nav_{_monday(date_str)}"),
            InlineKeyboardButton("🏠 Menú",   callback_data="menu_home"),
        ],
    ])


def _kb_back(date_str: str, prefix: str = "citas") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("← Volver al día", callback_data=f"{prefix}_nav_{date_str}"),
            InlineKeyboardButton("🏠 Menú",          callback_data="menu_home"),
        ],
    ])


def _monday(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return str(d - timedelta(days=d.weekday()))


def _kb_week_nav(monday_str: str) -> InlineKeyboardMarkup:
    d      = datetime.strptime(monday_str, "%Y-%m-%d").date()
    prev_w = str(d - timedelta(weeks=1))
    next_w = str(d + timedelta(weeks=1))
    this_w = str(date.today() - timedelta(days=date.today().weekday()))
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️ Semana ant.",  callback_data=f"semana_nav_{prev_w}"),
            InlineKeyboardButton("Semana sig. ▶️",  callback_data=f"semana_nav_{next_w}"),
        ],
        [
            InlineKeyboardButton("📅 Esta semana",  callback_data=f"semana_nav_{this_w}"),
            InlineKeyboardButton("🏠 Menú",          callback_data="menu_home"),
        ],
    ])


def _kb_start() -> InlineKeyboardMarkup:
    today = str(date.today())
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 Citas hoy",   callback_data=f"citas_nav_{today}"),
            InlineKeyboardButton("📊 Hábitos hoy", callback_data=f"habitos_nav_{today}"),
        ],
        [
            InlineKeyboardButton("📋 Semana",       callback_data=f"semana_nav_{_monday(today)}"),
        ],
        [
            InlineKeyboardButton("➕ Nueva cita",   callback_data="quick_nueva"),
            InlineKeyboardButton("➕ Nuevo hábito", callback_data="quick_habito"),
        ],
        [
            InlineKeyboardButton("⚙️ Config",       callback_data="quick_config"),
        ],
    ])


def _kb_tipos() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t.capitalize(), callback_data=f"tipo_{t}")] for t in TIPOS_CITA]
    )


def _kb_hab_value(cfg: Optional[dict]) -> Optional[InlineKeyboardMarkup]:
    if not cfg: return None
    habit_type = cfg.get("habit_type", "text")
    quick_vals = cfg.get("quick_vals", [])
    if habit_type == "boolean":
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sí", callback_data="hval_1"),
            InlineKeyboardButton("❌ No", callback_data="hval_0"),
        ]])
    if quick_vals:
        row, rows = [], []
        for val in quick_vals:
            row.append(InlineKeyboardButton(val, callback_data=f"hval_{val}"))
            if len(row) == 3:
                rows.append(row); row = []
        if row: rows.append(row)
        rows.append([InlineKeyboardButton("✏️ Otro valor", callback_data="hval___otro")])
        return InlineKeyboardMarkup(rows)
    return None


def _kb_apt_actions(date_str: str, index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑️ Borrar", callback_data=f"ad_{date_str}_{index}"),
        InlineKeyboardButton("✏️ Editar", callback_data=f"ae_{date_str}_{index}"),
    ]])


def _kb_apt_confirm(date_str: str, index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"adc_{date_str}_{index}"),
        InlineKeyboardButton("❌ Cancelar",   callback_data="cancel_action"),
    ]])


def _kb_hab_actions(date_str: str, habit: str) -> InlineKeyboardMarkup:
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑️", callback_data=f"hd_{date_str}_{h}"),
        InlineKeyboardButton("✏️", callback_data=f"he_{date_str}_{h}"),
        InlineKeyboardButton("➕", callback_data=f"ha_{date_str}_{h}"),
    ]])


def _kb_hab_confirm(date_str: str, habit: str) -> InlineKeyboardMarkup:
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"hdc_{date_str}_{h}"),
        InlineKeyboardButton("❌ Cancelar",   callback_data="cancel_action"),
    ]])


def _kb_hab_conflict(nombre: str, existing_val: str, new_val: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✏️ Sobreescribir", callback_data="hconf_overwrite"),
        InlineKeyboardButton("➕ Sumar",          callback_data="hconf_add"),
        InlineKeyboardButton("❌ Cancelar",       callback_data="hconf_cancel"),
    ]])


def _kb_conflict_apt(date_str: str, time: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Crear de todas formas", callback_data="aptconf_ok"),
        InlineKeyboardButton("❌ Cambiar hora",          callback_data="aptconf_change"),
    ]])


def _kb_cita_detail(date_str: str, index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Editar",  callback_data=f"ae_{date_str}_{index}"),
            InlineKeyboardButton("🗑️ Borrar", callback_data=f"ad_{date_str}_{index}"),
        ],
        [
            InlineKeyboardButton("← Volver al día", callback_data=f"citas_nav_{date_str}"),
        ],
    ])


# ════════════════════════════════════════════════════════════════════════
# /start — menú principal con saludo contextual
# ════════════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    today = str(date.today())
    greeting = _greeting()
    date_short = _date_short(today)
    try:
        apts_hoy = await api.get_appointments(today)
        n = len(apts_hoy)
        citas_txt = f"\n⏰ Tienes *{n} cita{'s' if n != 1 else ''}* hoy" if n else ""
    except Exception:
        citas_txt = ""
    await update.message.reply_text(
        f"{greeting}, soy *THDORA* — {date_short}{citas_txt}\n"
        f"_Tu asistente personal de gestión de vida_",
        parse_mode="Markdown",
        reply_markup=_kb_start(),
    )


async def cb_menu_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    today = str(date.today())
    greeting = _greeting()
    date_short = _date_short(today)
    try:
        apts_hoy = await api.get_appointments(today)
        n = len(apts_hoy)
        citas_txt = f"\n⏰ Tienes *{n} cita{'s' if n != 1 else ''}* hoy" if n else ""
    except Exception:
        citas_txt = ""
    await query.message.reply_text(
        f"{greeting}, soy *THDORA* — {date_short}{citas_txt}",
        parse_mode="Markdown",
        reply_markup=_kb_start(),
    )


async def cb_quick_dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botones rápidos desde /start y desde vistas de día."""
    query = update.callback_query
    await query.answer()
    data = query.data

    # ➕ Nueva cita
    if data == "quick_nueva" or data.startswith("quick_nueva_"):
        context.user_data.clear()
        if data.startswith("quick_nueva_"):
            fecha = data.replace("quick_nueva_", "")
            context.user_data["nueva_date"] = fecha
            await query.message.reply_text(
                f"📅 *Nueva cita para {_date_short(fecha)}*\n\n🕰 *Paso 1/4* — ¿A qué hora? `HH:MM`",
                parse_mode="Markdown",
            )
            return
        await query.message.reply_text(
            "📅 *Nueva cita — paso 1/5*\n\n¿Para qué fecha?\n`hoy`, `mañana`, `27/03`…",
            parse_mode="Markdown",
        )

    # ➕ Nuevo hábito — C2: sin lista predefinida, directo a nombre libre
    elif data == "quick_habito" or data.startswith("quick_habito_"):
        context.user_data.clear()
        if data.startswith("quick_habito_"):
            fecha = data.replace("quick_habito_", "")
            context.user_data["habito_date"] = fecha
        else:
            context.user_data["habito_date"] = str(date.today())
        fecha_label = _date_short(context.user_data["habito_date"])
        await query.message.reply_text(
            f"📊 *Nuevo hábito para {fecha_label}*\n\n✏️ *Paso 1/2* — ¿Cómo se llama el hábito?",
            parse_mode="Markdown",
        )

    elif data == "quick_config":
        await query.message.reply_text("⚙️ Usa /config para gestionar los tipos de hábitos.")


# ════════════════════════════════════════════════════════════════════════
# /citas con navegación ◀️▶️
# ════════════════════════════════════════════════════════════════════════

async def cmd_citas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clean_acum_context(context)
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_citas(update.message, date_str)


async def _show_citas(msg, date_str: str) -> None:
    try:
        apts = await api.get_appointments(date_str)
    except ApiError:
        await msg.reply_text("⚠️ Error al conectar con la API.")
        return

    label = _date_label(date_str)
    nav   = _nav_keyboard(date_str, "citas")

    if not apts:
        await msg.reply_text(
            f"📅 No hay citas el *{label}*\\.",
            parse_mode="Markdown",
            reply_markup=nav,
        )
        return

    await msg.reply_text(
        f"📅 *Citas del {label}:*",
        parse_mode="Markdown",
        reply_markup=nav,
    )

    for apt in apts:
        idx    = apt.get("index", 0)
        nombre = apt.get("name", "") or apt.get("type", "")
        notas  = f"\n📝 _{apt['notes']}_" if apt.get("notes") else ""
        await msg.reply_text(
            f"⏰ *{apt['time']}* — {nombre} \\[{apt['type']}\\]{notas}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"⏰ {apt['time']}",
                    callback_data=f"cita_detail_{date_str}_{idx}"
                ),
                InlineKeyboardButton("✏️", callback_data=f"ae_{date_str}_{idx}"),
                InlineKeyboardButton("🗑️", callback_data=f"ad_{date_str}_{idx}"),
            ]]),
        )


async def cb_citas_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str = query.data.replace("citas_nav_", "")
    await _show_citas(query.message, date_str)


async def cb_cita_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    parts    = query.data.split("_", 3)
    date_str = parts[2]
    idx      = int(parts[3])

    try:
        apts = await api.get_appointments(date_str)
    except ApiError:
        await query.message.reply_text("⚠️ Error al obtener la cita.")
        return

    apt = next((a for a in apts if a.get("index") == idx), None)
    if not apt:
        await query.message.reply_text(
            "⚠️ Cita no encontrada\\.",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
        return

    nombre = apt.get("name", "") or apt.get("type", "—")
    notas  = apt.get("notes") or "—"
    label  = _date_label(date_str)

    await query.message.reply_text(
        f"📅 *Detalle de cita*\n\n"
        f"  🗓 *Fecha:* {label}\n"
        f"  ⏰ *Hora:* {apt['time']}\n"
        f"  📝 *Nombre:* {nombre}\n"
        f"  🏷 *Tipo:* {apt['type']}\n"
        f"  💬 *Notas:* {notas}",
        parse_mode="Markdown",
        reply_markup=_kb_cita_detail(date_str, idx),
    )


# ════════════════════════════════════════════════════════════════════════
# /habitos con navegación ◀️▶️
# ════════════════════════════════════════════════════════════════════════

async def cmd_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clean_acum_context(context)
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    await _show_habitos(update.message, date_str)


async def _show_habitos(msg, date_str: str) -> None:
    try:
        habits = await api.get_habits(date_str)
    except ApiError:
        await msg.reply_text("⚠️ Error al conectar con la API.")
        return

    label = _date_label(date_str)
    nav   = _nav_keyboard(date_str, "habitos")

    if not habits:
        await msg.reply_text(
            f"📊 No hay hábitos el *{label}*\\.",
            parse_mode="Markdown",
            reply_markup=nav,
        )
        return

    await msg.reply_text(
        f"📊 *Hábitos del {label}:*",
        parse_mode="Markdown",
        reply_markup=nav,
    )
    for h, v in habits.items():
        await msg.reply_text(
            f"• *{h}*: `{v}`",
            parse_mode="Markdown",
            reply_markup=_kb_hab_actions(date_str, h),
        )


async def cb_habitos_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    date_str = query.data.replace("habitos_nav_", "")
    await _show_habitos(query.message, date_str)


# ════════════════════════════════════════════════════════════════════════
# /semana
# ════════════════════════════════════════════════════════════════════════

async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    monday = str(date.today() - timedelta(days=date.today().weekday()))
    await _show_semana(update.message, monday)


async def _show_semana(msg, monday_str: str) -> None:
    monday    = datetime.strptime(monday_str, "%Y-%m-%d").date()
    sunday    = monday + timedelta(days=6)
    today     = date.today()
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    months    = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

    lines = [f"📋 *Semana {monday.day} {months[monday.month-1]} — {sunday.day} {months[sunday.month-1]} {sunday.year}*\n"]
    btn_days = []
    total_apts   = 0
    days_habits  = 0

    for i in range(7):
        d     = monday + timedelta(days=i)
        d_str = str(d)
        dow   = day_names[i]
        mark  = " ◀ hoy" if d == today else ""
        try:
            apts   = await api.get_appointments(d_str)
            habits = await api.get_habits(d_str)
            apt_t  = f"📅{len(apts)}"   if apts   else "  —"
            hab_t  = f"📊{len(habits)}" if habits else "  —"
            total_apts  += len(apts)
            if habits: days_habits += 1
            lines.append(f"  {dow} {d.day:02d}  {apt_t}  {hab_t}{mark}")
        except ApiError:
            lines.append(f"  {dow} {d.day:02d}  ⚠️{mark}")
        btn_days.append(InlineKeyboardButton(
            f"{dow} {d.day}", callback_data=f"citas_nav_{d_str}"
        ))

    resumen = f"📅 {total_apts} citas  📊 {days_habits} días con hábitos"
    lines.insert(1, resumen)

    nav_kb = _kb_week_nav(monday_str)
    nav_rows = [list(row) for row in nav_kb.inline_keyboard]
    full_kb  = InlineKeyboardMarkup([btn_days[:4], btn_days[4:]] + nav_rows)
    await msg.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=full_kb)


async def cb_semana_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    monday_str = query.data.replace("semana_nav_", "")
    await _show_semana(query.message, monday_str)


# ════════════════════════════════════════════════════════════════════════
# CALLBACKS CITAS — borrar / editar
# ════════════════════════════════════════════════════════════════════════

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
        ok  = await api.delete_appointment(date_str, int(idx_str))
        txt = "🗑️ Cita eliminada\\." if ok else "⚠️ Cita no encontrada \\(ya borrada\\)\\."
        await query.edit_message_text(
            txt, parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
    except ApiError:
        await query.edit_message_text("⚠️ Error al borrar la cita\\.", parse_mode="Markdown")


async def cb_apt_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    context.user_data["edit_apt_date"]  = date_str
    context.user_data["edit_apt_index"] = int(idx_str)
    await query.edit_message_text(
        f"✏️ *Editar cita {idx_str} del {date_str}*\n\nNueva hora \\(HH:MM\\) o /skip:",
        parse_mode="Markdown",
    )
    return EDIT_APT_TIME


async def cb_apt_edit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() != "/skip":
        if not _RE_TIME.match(text):
            await update.message.reply_text("❌ Formato incorrecto\\. Usa `HH:MM` o /skip\\.", parse_mode="Markdown")
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
            + [[InlineKeyboardButton("⏭️ Skip", callback_data="etipo_skip")]]
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
    text     = update.message.text.strip()
    notes    = text if text.lower() != "/skip" else None
    date_str = context.user_data.get("edit_apt_date", "")
    index    = context.user_data.get("edit_apt_index", 0)
    try:
        await api.update_appointment(
            date_str, index,
            time=context.user_data.get("edit_apt_time"),
            name=context.user_data.get("edit_apt_nombre"),
            apt_type=context.user_data.get("edit_apt_type"),
            notes=notes,
        )
        await update.message.reply_text(
            f"✅ *Cita {index} actualizada\\.*",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
    except ApiError:
        await _reply_api_error(update)
    context.user_data.clear()
    return ConversationHandler.END


# ════════════════════════════════════════════════════════════════════════
# /nueva — ConversationHandler (5 pasos + conflicto)
# ════════════════════════════════════════════════════════════════════════

async def nueva_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "📅 *Nueva cita — paso 1/5*\n\n¿Para qué fecha?\n`hoy`, `mañana`, `27/03`…",
        parse_mode="Markdown",
    )
    return NUEVA_DATE


async def nueva_recv_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_str = _parse_date_flex(update.message.text.strip())
    if not date_str:
        await update.message.reply_text("❌ No entendí la fecha\\. Prueba `hoy`, `mañana` o `2026-03-27`\\.", parse_mode="Markdown")
        return NUEVA_DATE
    context.user_data["nueva_date"] = date_str
    await update.message.reply_text(
        f"✅ Fecha: *{date_str}*\n\n🕰 *Paso 2/5* — ¿A qué hora? \\(HH:MM, 24h\\)",
        parse_mode="Markdown",
    )
    return NUEVA_TIME


async def nueva_recv_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not _RE_TIME.match(text):
        await update.message.reply_text("❌ Formato incorrecto\\. Usa `HH:MM` \\(ej: `10:30`\\)\\.", parse_mode="Markdown")
        return NUEVA_TIME
    context.user_data["nueva_time"] = text
    date_str = context.user_data.get("nueva_date", str(date.today()))
    try:
        conflict = await api.check_appointment_conflict(date_str, text)
        if conflict:
            nc = conflict.get("name") or conflict.get("type", "cita")
            await update.message.reply_text(
                f"⚠️ *Ya tienes una cita a las {text}:* _{nc}_\n\n¿Crear de todas formas o cambiar hora?",
                parse_mode="Markdown",
                reply_markup=_kb_conflict_apt(date_str, text),
            )
            return NUEVA_CONFLICT
    except Exception:
        pass
    await update.message.reply_text(
        f"✅ Hora: *{text}*\n\n📝 *Paso 3/5* — ¿Cómo se llama la cita?",
        parse_mode="Markdown",
    )
    return NUEVA_NOMBRE


async def nueva_conflict_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "aptconf_ok":
        t = context.user_data.get("nueva_time", "")
        await query.edit_message_text(
            f"✅ Hora: *{t}*\n\n📝 *Paso 3/5* — ¿Cómo se llama la cita?",
            parse_mode="Markdown",
        )
        return NUEVA_NOMBRE
    await query.edit_message_text("🕰 Escribe la nueva hora \\(HH:MM\\):", parse_mode="Markdown")
    return NUEVA_TIME


async def nueva_recv_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return NUEVA_NOMBRE
    context.user_data["nueva_nombre"] = nombre
    await update.message.reply_text(
        f"✅ Nombre: *{nombre}*\n\n📋 *Paso 4/5* — ¿Tipo de cita?",
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
        f"✅ Tipo: *{apt_type}*\n\n📝 *Paso 5/5* — ¿Alguna nota? \\(/skip para omitir\\)",
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
        idx    = result.get("index", "?")
        await update.message.reply_text(
            f"✅ *Cita creada*\n\n"
            f"  📅 {d}  🕰 {t}\n"
            f"  📝 {nm} \\[{tp}\\]\n"
            f"  💬 {notes or '—'}",
            parse_mode="Markdown",
            reply_markup=_kb_back(d, "citas"),
        )
    except ApiError:
        await _reply_api_error(update)
    context.user_data.clear()
    return ConversationHandler.END


# ════════════════════════════════════════════════════════════════════════
# CALLBACKS HÁBITOS — borrar / editar / sumar
# ════════════════════════════════════════════════════════════════════════

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
        ok  = await api.delete_habit(date_str, habit)
        txt = "🗑️ Hábito eliminado\\." if ok else "⚠️ Hábito no encontrado \\(ya borrado\\)\\."
        await query.edit_message_text(
            txt, parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await query.edit_message_text("⚠️ Error al borrar el hábito\\.", parse_mode="Markdown")


async def cb_hab_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """C2: ahora pregunta primero el nuevo NOMBRE, luego el valor."""
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    context.user_data["edit_hab_date"]   = date_str
    context.user_data["edit_hab_nombre"] = habit
    await query.edit_message_text(
        f"✏️ *Editar hábito '{habit}'*\n\n"
        f"*Paso 1/2* — Nuevo nombre o /skip para mantener *'{habit}'*:",
        parse_mode="Markdown",
    )
    return EDIT_HAB_NOMBRE


async def cb_hab_edit_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """C2: recibe el nuevo nombre del hábito."""
    text = update.message.text.strip()
    if text.lower() != "/skip" and text:
        context.user_data["edit_hab_nombre_nuevo"] = text
    # Ahora pedir el valor
    habit = context.user_data.get("edit_hab_nombre", "")
    nuevo_nombre = context.user_data.get("edit_hab_nombre_nuevo", habit)
    try:
        cfg = await api.get_habit_config(nuevo_nombre)
    except Exception:
        cfg = None
    kb   = _kb_hab_value(cfg)
    hint = ""
    if cfg:
        htype = cfg.get("habit_type", "text")
        unit  = cfg.get("unit") or ""
        hint  = f" \\({HABIT_TYPE_EMOJIS.get(htype, '')} {htype}{' · ' + unit if unit else ''}\\)"
    prompt = f"✅ Nombre: *{nuevo_nombre}*{hint}\n\n*Paso 2/2* — Nuevo valor \\(/skip para mantener actual\\):"
    if kb:
        await update.message.reply_text(prompt, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(
            prompt + "\n\\(ej: `8h`, `30min`, `2L`\\)",
            parse_mode="Markdown",
        )
    return EDIT_HAB_VALUE


async def cb_hab_edit_value_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("hval_", "")
    if value == "__otro":
        await query.edit_message_text("✏️ Escribe el nuevo valor:")
        return EDIT_HAB_VALUE
    return await _do_edit_habit(query.message, context, value)


async def cb_hab_edit_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() == "/skip":
        return await _do_edit_habit(update.message, context, None)
    return await _do_edit_habit(update.message, context, text)


async def _do_edit_habit(msg, context, value: Optional[str]) -> int:
    """C2: actualiza nombre y/o valor del hábito."""
    date_str      = context.user_data.get("edit_hab_date", "")
    nombre_orig   = context.user_data.get("edit_hab_nombre", "")
    nombre_nuevo  = context.user_data.get("edit_hab_nombre_nuevo", nombre_orig)
    try:
        # Si cambió el nombre: borrar el viejo y crear con nuevo nombre
        if nombre_nuevo != nombre_orig:
            habits   = await api.get_habits(date_str)
            val_orig = habits.get(nombre_orig)
            final_val = value if value else val_orig
            await api.delete_habit(date_str, nombre_orig)
            await api.log_habit(date_str, nombre_nuevo, final_val or "")
        else:
            if value:
                await api.update_habit(date_str, nombre_orig, value)
            final_val = value or "sin cambios"

        cambios = []
        if nombre_nuevo != nombre_orig:
            cambios.append(f"  📝 Nombre: *{nombre_orig}* → *{nombre_nuevo}*")
        if value:
            cambios.append(f"  📊 Valor: `{final_val}`")
        if not cambios:
            cambios.append("  _Sin cambios_")

        await msg.reply_text(
            f"✅ *Hábito actualizado*\n\n" + "\n".join(cambios),
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await msg.reply_text("⚠️ Error al actualizar el hábito.")
    context.user_data.clear()
    return ConversationHandler.END


async def cb_hab_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    context.user_data["acum_hab_date"]   = date_str
    context.user_data["acum_hab_nombre"] = habit
    await query.edit_message_text(
        f"➕ *Sumar a '{habit}'*\n\n"
        "Incremento \\(ej: `+2`, `+30min`, `+1.5L`\\)\n"
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
        habits      = await api.get_habits(date_str)
        existing    = habits.get(habit)
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, habit, final_value)
        op = "acumulado" if new_input.startswith("+") else "actualizado"
        await update.message.reply_text(
            f"✅ *{habit}* {op}: `{existing or '0'}` → `{final_value}`",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await _reply_api_error(update)
    _clean_acum_context(context)


# ════════════════════════════════════════════════════════════════════════
# /habito — ConversationHandler C2 (nombre libre, sin lista predefinida)
# ════════════════════════════════════════════════════════════════════════

async def habito_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["habito_date"] = str(date.today())
    fecha_label = _date_short(str(date.today()))
    await update.message.reply_text(
        f"📊 *Nuevo hábito para {fecha_label}*\n\n✏️ *Paso 1/2* — ¿Cómo se llama el hábito?",
        parse_mode="Markdown",
    )
    return HABITO_NOMBRE


async def habito_recv_nombre_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío\\.", parse_mode="Markdown")
        return HABITO_NOMBRE
    context.user_data["habito_nombre"] = nombre
    return await _ask_habito_value(update.message, context, nombre)


async def _ask_habito_value(msg, context, nombre: str) -> int:
    try:
        cfg = await api.get_habit_config(nombre)
    except Exception:
        cfg = None
    kb   = _kb_hab_value(cfg)
    hint = ""
    if cfg:
        htype = cfg.get("habit_type", "text")
        unit  = cfg.get("unit") or ""
        hint  = f" \\({HABIT_TYPE_EMOJIS.get(htype, '')} {htype}{' · ' + unit if unit else ''}\\)"
    prompt = f"✅ Hábito: *{nombre}*{hint}\n\n📊 *Paso 2/2* — ¿Cuál es el valor?"
    if kb:
        await msg.reply_text(prompt, parse_mode="Markdown", reply_markup=kb)
    else:
        await msg.reply_text(
            prompt + " \\(ej: `8h`, `30min`, `2L`\\)\nUsa `+N` para acumular\\.",
            parse_mode="Markdown",
        )
    return HABITO_VALUE


async def habito_recv_value_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.replace("hval_", "")
    if value == "__otro":
        await query.edit_message_text("✏️ Escribe el valor:")
        return HABITO_VALUE
    return await _save_habito(query.message, context, value)


async def habito_recv_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    if not value:
        await update.message.reply_text("❌ El valor no puede estar vacío\\.", parse_mode="Markdown")
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
                f"⚠️ *{nombre}* ya tiene `{existing}` hoy\\.\n¿Qué haces con `{new_input}`?",
                parse_mode="Markdown",
                reply_markup=_kb_hab_conflict(nombre, existing, new_input),
            )
            return HABITO_CONFLICT
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, nombre, final_value)
        extra = f"\n  \\({existing} + {new_input[1:]} = {final_value}\\)" if new_input.startswith("+") and existing else ""
        await msg.reply_text(
            f"✅ *Hábito registrado*\n\n"
            f"  📊 {nombre}: `{final_value}`\n"
            f"  📅 {date_str}{extra}",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await _reply_api_error_msg(msg)
    context.user_data.clear()
    return ConversationHandler.END


async def habito_conflict_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query    = update.callback_query
    await query.answer()
    nombre   = context.user_data.get("habito_nombre", "")
    date_str = context.user_data.get("habito_date", str(date.today()))
    new_val  = context.user_data.get("habito_new_val", "")
    existing = context.user_data.get("habito_existing_val", "")
    if query.data == "hconf_cancel":
        await query.edit_message_text(
            "❌ Operación cancelada\\.",
            reply_markup=_kb_back(date_str, "habitos"),
        )
        context.user_data.clear()
        return ConversationHandler.END
    final_value = _accumulate_value(existing, f"+{new_val}") if query.data == "hconf_add" else new_val
    try:
        await api.log_habit(date_str, nombre, final_value)
        op = "sumado" if query.data == "hconf_add" else "sobreescrito"
        await query.edit_message_text(
            f"✅ *{nombre}* {op}: `{existing}` → `{final_value}`",
            parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "habitos"),
        )
    except ApiError:
        await query.edit_message_text("⚠️ Error al guardar el hábito.")
    context.user_data.clear()
    return ConversationHandler.END


# ════════════════════════════════════════════════════════════════════════
# /config
# ════════════════════════════════════════════════════════════════════════

async def cmd_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        configs = await api.get_all_habit_configs()
    except Exception:
        configs = []
    if configs:
        lines = ["⚙️ *Configuración de hábitos:*\n"]
        for c in configs:
            emoji = HABIT_TYPE_EMOJIS.get(c["habit_type"], "📝")
            unit  = f" ({c['unit']})" if c.get("unit") else ""
            quick = ", ".join(c["quick_vals"]) if c.get("quick_vals") else "texto libre"
            lines.append(f"  {emoji} *{c['name']}*{unit} — {c['habit_type']}\n     Botones: {quick}")
        text = "\n".join(lines)
    else:
        text = "⚙️ No hay ningún hábito configurado todavía\\."
    await update.message.reply_text(
        text + "\n\n➕ Escribe el nombre del hábito a configurar:",
        parse_mode="Markdown",
    )
    return CFG_NOMBRE


async def cfg_recv_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío.")
        return CFG_NOMBRE
    context.user_data["cfg_nombre"] = nombre
    await update.message.reply_text(
        f"⚙️ Configurando: *{nombre}*\n\n¿Qué tipo de hábito es?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔢 Numérico", callback_data="cfgt_numeric"),
            InlineKeyboardButton("⏱️ Tiempo",   callback_data="cfgt_time"),
        ], [
            InlineKeyboardButton("✅ Sí/No",    callback_data="cfgt_boolean"),
            InlineKeyboardButton("📝 Texto",    callback_data="cfgt_text"),
        ]])
    )
    return CFG_TYPE


async def cfg_recv_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    habit_type = query.data.replace("cfgt_", "")
    context.user_data["cfg_type"] = habit_type
    if habit_type == "boolean":
        await _save_habit_config(query.message, context, None, None)
        return ConversationHandler.END
    await query.edit_message_text(
        f"✅ Tipo: *{habit_type}*\n\n¿Unidad? \\(ej: `h`, `min`, `L`\\) o /skip:",
        parse_mode="Markdown",
    )
    return CFG_UNIT


async def cfg_recv_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["cfg_unit"] = None if text.lower() == "/skip" else text
    await update.message.reply_text(
        "🚀 Botones rápidos: valores separados por comas \\(ej: `6h,7h,8h`\\) o /skip:"
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
        await api.upsert_habit_config(name=nombre, habit_type=habit_type, unit=unit, quick_vals=quick_vals)
        quick_str = ", ".join(quick_vals) if quick_vals else "texto libre"
        await msg.reply_text(
            f"✅ *{nombre}* configurado:\n  Tipo: {habit_type}  Unidad: {unit or '—'}\n  Botones: {quick_str}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await msg.reply_text(f"⚠️ Error al guardar la config: {e}")
    context.user_data.clear()


# ════════════════════════════════════════════════════════════════════════
# /resumen
# ════════════════════════════════════════════════════════════════════════

async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        summary = await api.get_summary(date_str)
        apts    = summary.get("appointments", [])
        habits  = summary.get("habits", {})
        label   = _date_label(date_str)
        text = (
            f"📋 *Resumen del {label}*\n\n"
            + _fmt_appointments(apts, date_str)
            + "\n\n"
            + _fmt_habits(habits, date_str)
        )
        await update.message.reply_text(
            text, parse_mode="Markdown",
            reply_markup=_kb_back(date_str, "citas"),
        )
    except ApiError:
        await _reply_api_error(update)


# ════════════════════════════════════════════════════════════════════════
# /cancelar
# ════════════════════════════════════════════════════════════════════════

async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Operación cancelada\\.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Menú", callback_data="menu_home")
        ]])
    )
    return ConversationHandler.END


async def cb_cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("Cancelado")
    await query.delete_message()


# ════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ════════════════════════════════════════════════════════════════════════

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Error no controlado en update %s: %s", update, context.error, exc_info=True)


async def _reply_api_error(update: Update) -> None:
    msg = update.message or (update.callback_query.message if update.callback_query else None)
    if msg:
        await msg.reply_text(
            "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
            parse_mode="Markdown",
        )


async def _reply_api_error_msg(msg) -> None:
    await msg.reply_text(
        "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
        parse_mode="Markdown",
    )


# ════════════════════════════════════════════════════════════════════════
# FACTORIES DE CONVERSATIONHANDLER
# ════════════════════════════════════════════════════════════════════════

def build_nueva_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("nueva", nueva_start)],
        states={
            NUEVA_DATE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_date)],
            NUEVA_TIME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_time)],
            NUEVA_CONFLICT: [CallbackQueryHandler(nueva_conflict_response, pattern=r"^aptconf_")],
            NUEVA_NOMBRE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_nombre)],
            NUEVA_TYPE:     [CallbackQueryHandler(nueva_recv_type, pattern=r"^tipo_")],
            NUEVA_NOTES: [
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
            EDIT_APT_TIME: [
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
    """C2: ahora incluye EDIT_HAB_NOMBRE antes de EDIT_HAB_VALUE."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_hab_edit_start, pattern=r"^he_")],
        states={
            EDIT_HAB_NOMBRE: [
                CommandHandler("skip", lambda u, c: cb_hab_edit_nombre(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_hab_edit_nombre),
            ],
            EDIT_HAB_VALUE: [
                CallbackQueryHandler(cb_hab_edit_value_inline, pattern=r"^hval_"),
                CommandHandler("skip", lambda u, c: cb_hab_edit_value_text(u, c)),
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
            CFG_UNIT: [
                CommandHandler("skip", lambda u, c: cfg_recv_unit(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_unit),
            ],
            CFG_QUICK: [
                CommandHandler("skip", lambda u, c: cfg_recv_quick(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cfg_recv_quick),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="config_habito", persistent=False, per_message=False,
    )


async def _skip_to(update, context, next_state, prompt):
    await update.message.reply_text(prompt)
    return next_state

async def _skip_to_type(update, context):
    await update.message.reply_text(
        "Nuevo tipo o /skip:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(t.capitalize(), callback_data=f"etipo_{t}") for t in TIPOS_CITA]]
            + [[InlineKeyboardButton("⏭️ Skip", callback_data="etipo_skip")]]
        )
    )
    return EDIT_APT_TYPE
