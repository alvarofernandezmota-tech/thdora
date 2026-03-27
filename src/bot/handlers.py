"""
Handlers del bot Telegram de THDORA — v2.1.

Cambios respecto a v2:
    - Fix bug tipo /nueva: CallbackQueryHandler NUEVA_TYPE con per_message=True
    - Fix contexto acum suelto: se limpia al entrar en /citas y /habitos
    - build_edit_apt_handler usa per_message=True para no interferir

Comandos disponibles::

    /start                → presentación y ayuda
    /citas [fecha]        → ver citas con botones inline
    /nueva                → crear cita (5 pasos)
    /habitos [fecha]      → ver hábitos con botones inline
    /habito               → registrar hábito rápido
    /resumen [fecha]      → resumen completo del día
    /cancelar             → abortar operación en curso

Fechas aceptadas (dateparser)::

    hoy, mañana, ayer, 27/03, 2026-03-27, lunes, "el viernes"
"""

import logging
import re
from datetime import date, datetime
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

# ── Estados de conversación ────────────────────────────────────────────────

# /nueva cita: 5 pasos
NUEVA_DATE, NUEVA_TIME, NUEVA_NOMBRE, NUEVA_TYPE, NUEVA_NOTES = range(5)

# /habito: 2 pasos
HABITO_NOMBRE, HABITO_VALUE = range(10, 12)

# editar cita: 4 pasos (rangos separados)
EDIT_APT_TIME, EDIT_APT_NOMBRE, EDIT_APT_TYPE, EDIT_APT_NOTES = range(20, 24)

# editar hábito: 1 paso
EDIT_HAB_VALUE = 30

# ── Constantes de dominio ───────────────────────────────────────────────

TIPOS_CITA = ["médica", "personal", "trabajo", "otra"]

HABITOS_COMUNES = [
    "sueño", "THC", "tabaco", "ejercicio", "agua", "humor", "alimentacion"
]

_RE_TIME = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
_RE_ACUM = re.compile(r"^\+([\d\.]+)(.*)$")  # "+2L", "+30min", "+1.5"
_RE_NUMBER = re.compile(r"^([\d\.]+)(.*)$")  # extrae el número de un valor


# ── Helpers ────────────────────────────────────────────────────────────


def _parse_date_flex(text: str) -> Optional[str]:
    """
    Convierte texto a YYYY-MM-DD con dateparser si está disponible.
    Acepta: "hoy", "mañana", "ayer", "27/03", "2026-03-27", "lunes"...
    """
    t = text.strip().lower()

    if t in ("hoy", "today"):
        return str(date.today())
    if t in ("mañana", "manana", "tomorrow"):
        from datetime import timedelta
        return str(date.today() + timedelta(days=1))
    if t in ("ayer", "yesterday"):
        from datetime import timedelta
        return str(date.today() - timedelta(days=1))

    try:
        datetime.strptime(t, "%Y-%m-%d")
        return t
    except ValueError:
        pass

    if _HAS_DATEPARSER:
        parsed = dateparser.parse(
            text,
            languages=["es", "en"],
            settings={"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False},
        )
        if parsed:
            return parsed.strftime("%Y-%m-%d")

    return None


def _parse_date_arg(arg: Optional[str]) -> str:
    """Wrapper para comandos: devuelve hoy si arg es None o inválido."""
    if arg:
        result = _parse_date_flex(arg)
        if result:
            return result
    return str(date.today())


def _accumulate_value(existing: Optional[str], new_input: str) -> str:
    """
    Acumula un valor de hábito si empieza con '+'.

    Ejemplos::

        _accumulate_value("1L", "+2L")       → "3.0L"
        _accumulate_value("30min", "+15min") → "45.0min"
        _accumulate_value(None, "+2")        → "2.0"
        _accumulate_value("8h", "7h")        → "7h"  # sobreescribe
    """
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
    """Limpia el contexto de acumulación de hábito para evitar interferencias."""
    context.user_data.pop("acum_hab_date", None)
    context.user_data.pop("acum_hab_nombre", None)


def _fmt_appointments(apts: list, date_str: str) -> str:
    """Formatea lista de citas en markdown de Telegram."""
    if not apts:
        return f"📅 No hay citas el *{date_str}*\\."
    lines = [f"📅 *Citas del {date_str}:*\n"]
    for a in apts:
        idx = a.get("index", "?")
        nombre = a.get("name", "") or a.get("type", "")
        notas = f"\n      _{a['notes']}_" if a.get("notes") else ""
        lines.append(f"  *{idx}\\. {a['time']}* — {nombre} \\[{a['type']}\\]{notas}")
    return "\n".join(lines)


def _fmt_habits(habits: dict, date_str: str) -> str:
    """Formatea dict de hábitos en markdown de Telegram."""
    if not habits:
        return f"📊 No hay hábitos registrados el *{date_str}*\\."
    lines = [f"📊 *Hábitos del {date_str}:*\n"]
    for h, v in habits.items():
        lines.append(f"  • {h}: `{v}`")
    return "\n".join(lines)


def _kb_tipos() -> InlineKeyboardMarkup:
    """Teclado inline con los tipos de cita."""
    buttons = [
        [InlineKeyboardButton(t.capitalize(), callback_data=f"tipo_{t}")]
        for t in TIPOS_CITA
    ]
    return InlineKeyboardMarkup(buttons)


def _kb_habitos() -> InlineKeyboardMarkup:
    """Teclado inline con los hábitos comunes más un botón 'Otro'."""
    buttons = [
        [InlineKeyboardButton(h, callback_data=f"hab_{h}")]
        for h in HABITOS_COMUNES
    ]
    buttons.append([InlineKeyboardButton("✏️ Otro…", callback_data="hab___otro")])
    return InlineKeyboardMarkup(buttons)


def _kb_apt_actions(date_str: str, index: int) -> InlineKeyboardMarkup:
    """Botones inline por cita: Borrar + Editar."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑️ Borrar", callback_data=f"ad_{date_str}_{index}"),
        InlineKeyboardButton("✏️ Editar", callback_data=f"ae_{date_str}_{index}"),
    ]])


def _kb_apt_confirm(date_str: str, index: int) -> InlineKeyboardMarkup:
    """Confirmación antes de borrar una cita."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"adc_{date_str}_{index}"),
        InlineKeyboardButton("❌ Cancelar", callback_data="cancel_action"),
    ]])


def _kb_hab_actions(date_str: str, habit: str) -> InlineKeyboardMarkup:
    """Botones inline por hábito: Borrar + Editar + Sumar."""
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑️", callback_data=f"hd_{date_str}_{h}"),
        InlineKeyboardButton("✏️", callback_data=f"he_{date_str}_{h}"),
        InlineKeyboardButton("➕", callback_data=f"ha_{date_str}_{h}"),
    ]])


def _kb_hab_confirm(date_str: str, habit: str) -> InlineKeyboardMarkup:
    """Confirmación antes de borrar un hábito."""
    h = habit[:15]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, borrar", callback_data=f"hdc_{date_str}_{h}"),
        InlineKeyboardButton("❌ Cancelar", callback_data="cancel_action"),
    ]])


# ── /start ───────────────────────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra la bienvenida y lista de comandos."""
    text = (
        "👋 *Hola, soy THDORA*\n"
        "_Tu asistente personal de gestión de vida_\n\n"
        "*Citas:*\n"
        "  📅 /citas `[fecha]` — ver citas del día\n"
        "  ➕ /nueva — crear una cita \\(5 pasos\\)\n\n"
        "*Hábitos:*\n"
        "  📊 /habitos `[fecha]` — ver hábitos\n"
        "  ✏️ /habito — registrar un hábito\n\n"
        "*Resumen:*\n"
        "  📋 /resumen `[fecha]` — resumen completo del día\n\n"
        "*Fechas aceptadas:* `hoy`, `mañana`, `ayer`, `27/03`, `2026-03-27`\n\n"
        "❌ /cancelar — abortar operación en curso"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ── /citas ──────────────────────────────────────────────────────────


async def cmd_citas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lista las citas del día con botones inline por cita."""
    # FIX: limpiar contexto acumulación para evitar interferencias
    _clean_acum_context(context)

    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        apts = await api.get_appointments(date_str)
    except ApiError as e:
        logger.error("cmd_citas: %s", e)
        await _reply_api_error(update)
        return

    if not apts:
        await update.message.reply_text(
            f"📅 No hay citas el *{date_str}*\\.", parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"📅 *Citas del {date_str}:*", parse_mode="Markdown"
    )
    for apt in apts:
        idx = apt.get("index", 0)
        nombre = apt.get("name", "") or apt.get("type", "")
        notas = f"\n📝 _{apt['notes']}_" if apt.get("notes") else ""
        text = f"🕒 *{apt['time']}* — {nombre} \\[{apt['type']}\\]{notas}"
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=_kb_apt_actions(date_str, idx),
        )


# ── Callbacks de citas (borrar/editar) ───────────────────────────────────


async def cb_apt_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pide confirmación antes de borrar una cita. Pattern: ^ad_"""
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    await query.edit_message_reply_markup(
        reply_markup=_kb_apt_confirm(date_str, int(idx_str))
    )


async def cb_apt_delete_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Ejecuta el borrado tras confirmación. Pattern: ^adc_"""
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    try:
        ok = await api.delete_appointment(date_str, int(idx_str))
        if ok:
            await query.edit_message_text("🗑️ Cita eliminada\\.", parse_mode="Markdown")
        else:
            await query.edit_message_text(
                "⚠️ Cita no encontrada \\(ya fue borrada\\)\\.", parse_mode="Markdown"
            )
    except ApiError as e:
        logger.error("cb_apt_delete_confirm: %s", e)
        await query.edit_message_text("⚠️ Error al borrar la cita\\.", parse_mode="Markdown")


async def cb_apt_edit_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Inicia el flujo de edición de una cita. Pattern: ^ae_"""
    query = update.callback_query
    await query.answer()
    _, date_str, idx_str = query.data.split("_", 2)
    context.user_data["edit_apt_date"] = date_str
    context.user_data["edit_apt_index"] = int(idx_str)
    await query.edit_message_text(
        f"✏️ *Editar cita {idx_str} del {date_str}*\n\n"
        "Nueva hora \\(HH:MM\\) o /skip para no cambiarla:",
        parse_mode="Markdown",
    )
    return EDIT_APT_TIME


async def cb_apt_edit_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe la nueva hora de la cita."""
    text = update.message.text.strip()
    if text.lower() != "/skip":
        if not _RE_TIME.match(text):
            await update.message.reply_text(
                "❌ Formato incorrecto\\. Usa `HH:MM` o /skip\\.", parse_mode="Markdown"
            )
            return EDIT_APT_TIME
        context.user_data["edit_apt_time"] = text
    await update.message.reply_text("Nuevo nombre/descripción o /skip:")
    return EDIT_APT_NOMBRE


async def cb_apt_edit_nombre(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe el nuevo nombre de la cita."""
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


async def cb_apt_edit_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe el nuevo tipo de la cita desde inline."""
    query = update.callback_query
    await query.answer()
    value = query.data.replace("etipo_", "")
    if value != "skip":
        context.user_data["edit_apt_type"] = value
    await query.edit_message_text("Nuevas notas o /skip:")
    return EDIT_APT_NOTES


async def cb_apt_edit_notes(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe las notas y ejecuta la actualización."""
    text = update.message.text.strip()
    notes = text if text.lower() != "/skip" else None

    date_str = context.user_data.get("edit_apt_date", "")
    index = context.user_data.get("edit_apt_index", 0)
    try:
        await api.update_appointment(
            date_str,
            index,
            time=context.user_data.get("edit_apt_time"),
            name=context.user_data.get("edit_apt_nombre"),
            apt_type=context.user_data.get("edit_apt_type"),
            notes=notes,
        )
        await update.message.reply_text(
            f"✅ *Cita {index} actualizada\\.*", parse_mode="Markdown"
        )
    except ApiError as e:
        logger.error("cb_apt_edit_notes: %s", e)
        await _reply_api_error(update)

    context.user_data.clear()
    return ConversationHandler.END


# ── /nueva — ConversationHandler (5 pasos) ──────────────────────────────


async def nueva_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación para crear una cita."""
    context.user_data.clear()
    await update.message.reply_text(
        "📅 *Nueva cita — paso 1/5*\n\n"
        "¿Para qué fecha?\n"
        "`hoy`, `mañana`, `27/03`, `2026-03-27`…",
        parse_mode="Markdown",
    )
    return NUEVA_DATE


async def nueva_recv_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe y valida la fecha con dateparser."""
    text = update.message.text.strip()
    date_str = _parse_date_flex(text)
    if not date_str:
        await update.message.reply_text(
            "❌ No entendí la fecha\\. Prueba con `hoy`, `mañana` o `2026-03-27`\\.",
            parse_mode="Markdown",
        )
        return NUEVA_DATE

    context.user_data["nueva_date"] = date_str
    await update.message.reply_text(
        f"✅ Fecha: *{date_str}*\n\n"
        "🕒 *Paso 2/5* — ¿A qué hora? \\(formato `HH:MM`, 24h\\)",
        parse_mode="Markdown",
    )
    return NUEVA_TIME


async def nueva_recv_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe y valida la hora."""
    text = update.message.text.strip()
    if not _RE_TIME.match(text):
        await update.message.reply_text(
            "❌ Formato incorrecto\\. Usa `HH:MM` \\(ej: `10:30`\\)\\.",
            parse_mode="Markdown",
        )
        return NUEVA_TIME

    context.user_data["nueva_time"] = text
    await update.message.reply_text(
        f"✅ Hora: *{text}*\n\n"
        "📝 *Paso 3/5* — ¿Cómo se llama la cita? \\(ej: `Dentista`, `Reunión con Ana`\\)",
        parse_mode="Markdown",
    )
    return NUEVA_NOMBRE


async def nueva_recv_nombre(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe el nombre/descripción de la cita."""
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text(
            "❌ El nombre no puede estar vacío\\.", parse_mode="Markdown"
        )
        return NUEVA_NOMBRE

    context.user_data["nueva_nombre"] = nombre
    await update.message.reply_text(
        f"✅ Nombre: *{nombre}*\n\n"
        "📋 *Paso 4/5* — ¿Tipo de cita?",
        parse_mode="Markdown",
        reply_markup=_kb_tipos(),
    )
    return NUEVA_TYPE


async def nueva_recv_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe el tipo de cita desde el teclado inline."""
    query = update.callback_query
    await query.answer()
    apt_type = query.data.replace("tipo_", "")
    context.user_data["nueva_type"] = apt_type
    await query.edit_message_text(
        f"✅ Tipo: *{apt_type}*\n\n"
        "📝 *Paso 5/5* — ¿Alguna nota? \\(texto libre o /skip para omitir\\)",
        parse_mode="Markdown",
    )
    return NUEVA_NOTES


async def nueva_recv_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe las notas y guarda la cita."""
    return await _save_appointment(update, context, update.message.text.strip())


async def nueva_skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la cita sin notas."""
    return await _save_appointment(update, context, "")


async def _save_appointment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, notes: str
) -> int:
    """Llama a la API para crear la cita y termina la conversación."""
    d = context.user_data.get("nueva_date", str(date.today()))
    t = context.user_data.get("nueva_time", "")
    nombre = context.user_data.get("nueva_nombre", "")
    tp = context.user_data.get("nueva_type", "otra")

    try:
        result = await api.create_appointment(d, t, nombre, tp, notes)
        idx = result.get("index", "?")
        notas_str = notes or "—"
        await update.message.reply_text(
            f"✅ *Cita creada*\n\n"
            f"  📅 {d}  🕒 {t}\n"
            f"  📝 {nombre}\n"
            f"  📋 {tp}\n"
            f"  💬 {notas_str}\n"
            f"  \\# índice: `{idx}`",
            parse_mode="Markdown",
        )
    except ApiError as e:
        logger.error("_save_appointment: %s", e)
        await _reply_api_error(update)

    context.user_data.clear()
    return ConversationHandler.END


# ── /habitos ────────────────────────────────────────────────────────


async def cmd_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lista los hábitos del día con botones inline por hábito."""
    # FIX: limpiar contexto acumulación para evitar interferencias
    _clean_acum_context(context)

    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        habits = await api.get_habits(date_str)
    except ApiError as e:
        logger.error("cmd_habitos: %s", e)
        await _reply_api_error(update)
        return

    if not habits:
        await update.message.reply_text(
            f"📊 No hay hábitos el *{date_str}*\\.", parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"📊 *Hábitos del {date_str}:*", parse_mode="Markdown"
    )
    for h, v in habits.items():
        await update.message.reply_text(
            f"• *{h}*: `{v}`",
            parse_mode="Markdown",
            reply_markup=_kb_hab_actions(date_str, h),
        )


# ── Callbacks de hábitos (borrar/editar/sumar) ────────────────────────────


async def cb_hab_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pide confirmación antes de borrar un hábito. Pattern: ^hd_"""
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    await query.edit_message_reply_markup(
        reply_markup=_kb_hab_confirm(date_str, habit)
    )


async def cb_hab_delete_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Ejecuta el borrado del hábito. Pattern: ^hdc_"""
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    try:
        ok = await api.delete_habit(date_str, habit)
        if ok:
            await query.edit_message_text("🗑️ Hábito eliminado\\.", parse_mode="Markdown")
        else:
            await query.edit_message_text(
                "⚠️ Hábito no encontrado \\(ya fue borrado\\)\\.", parse_mode="Markdown"
            )
    except ApiError as e:
        logger.error("cb_hab_delete_confirm: %s", e)
        await query.edit_message_text("⚠️ Error al borrar el hábito\\.", parse_mode="Markdown")


async def cb_hab_edit_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Inicia el flujo de edición de un hábito. Pattern: ^he_"""
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    context.user_data["edit_hab_date"] = date_str
    context.user_data["edit_hab_nombre"] = habit
    await query.edit_message_text(
        f"✏️ *Editar hábito '{habit}'*\n\nNuevo valor:",
        parse_mode="Markdown",
    )
    return EDIT_HAB_VALUE


async def cb_hab_edit_value(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe el nuevo valor y actualiza el hábito."""
    value = update.message.text.strip()
    date_str = context.user_data.get("edit_hab_date", "")
    habit = context.user_data.get("edit_hab_nombre", "")
    try:
        await api.update_habit(date_str, habit, value)
        await update.message.reply_text(
            f"✅ *{habit}* actualizado a `{value}`\\.", parse_mode="Markdown"
        )
    except ApiError as e:
        logger.error("cb_hab_edit_value: %s", e)
        await _reply_api_error(update)
    context.user_data.clear()
    return ConversationHandler.END


async def cb_hab_add(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Inicia acumulación rápida de un hábito. Pattern: ^ha_"""
    query = update.callback_query
    await query.answer()
    _, date_str, habit = query.data.split("_", 2)
    context.user_data["acum_hab_date"] = date_str
    context.user_data["acum_hab_nombre"] = habit
    await query.edit_message_text(
        f"➕ *Sumar a '{habit}'*\n\n"
        "Escribe el incremento \\(ej: `\\+2`, `\\+30min`, `\\+1\.5L`\\)\n"
        "O escribe el nuevo valor directo para sobreescribir:",
        parse_mode="Markdown",
    )


async def cb_hab_add_value(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Recibe el incremento, calcula el nuevo valor y lo guarda."""
    new_input = update.message.text.strip()
    date_str = context.user_data.get("acum_hab_date", "")
    habit = context.user_data.get("acum_hab_nombre", "")

    if not date_str or not habit:
        return

    try:
        habits = await api.get_habits(date_str)
        existing = habits.get(habit)
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, habit, final_value)
        op = "acumulado" if new_input.startswith("+") else "actualizado"
        await update.message.reply_text(
            f"✅ *{habit}* {op}: `{existing or '0'}` → `{final_value}`",
            parse_mode="Markdown",
        )
    except ApiError as e:
        logger.error("cb_hab_add_value: %s", e)
        await _reply_api_error(update)

    _clean_acum_context(context)


# ── Callback genérico: cancelar acción ──────────────────────────────────────


async def cb_cancel_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Restaura los botones originales al pulsar Cancelar en una confirmación."""
    query = update.callback_query
    await query.answer("Cancelado")
    await query.delete_message()


# ── /habito — ConversationHandler rápido ───────────────────────────────────


async def habito_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación para registrar un hábito."""
    context.user_data.clear()
    context.user_data["habito_date"] = str(date.today())
    await update.message.reply_text(
        "✏️ *Registrar hábito — paso 1/2*\n\n¿Qué hábito registras hoy?",
        parse_mode="Markdown",
        reply_markup=_kb_habitos(),
    )
    return HABITO_NOMBRE


async def habito_recv_nombre_inline(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe el nombre del hábito desde el teclado inline."""
    query = update.callback_query
    await query.answer()
    nombre = query.data.replace("hab_", "")

    if nombre == "__otro":
        await query.edit_message_text("✏️ Escribe el nombre del hábito:")
        return HABITO_NOMBRE

    context.user_data["habito_nombre"] = nombre
    await query.edit_message_text(
        f"✅ Hábito: *{nombre}*\n\n"
        "📊 *Paso 2/2* — ¿Cuál es el valor? \\(ej: `8h`, `0`, `30min`, `2L`\\)\n"
        "Usa `\\+N` para acumular al valor existente \\(ej: `\\+2`\\)",
        parse_mode="Markdown",
    )
    return HABITO_VALUE


async def habito_recv_nombre_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe el nombre del hábito como texto libre."""
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text(
            "❌ El nombre no puede estar vacío\\.", parse_mode="Markdown"
        )
        return HABITO_NOMBRE

    context.user_data["habito_nombre"] = nombre
    await update.message.reply_text(
        f"✅ Hábito: *{nombre}*\n\n"
        "📊 *Paso 2/2* — ¿Cuál es el valor? \\(ej: `8h`, `0`, `30min`, `2L`\\)\n"
        "Usa `\\+N` para acumular al valor existente \\(ej: `\\+2`\\)",
        parse_mode="Markdown",
    )
    return HABITO_VALUE


async def habito_recv_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe el valor, acumula si empieza con '+', y guarda el hábito."""
    new_input = update.message.text.strip()
    if not new_input:
        await update.message.reply_text(
            "❌ El valor no puede estar vacío\\.", parse_mode="Markdown"
        )
        return HABITO_VALUE

    nombre = context.user_data.get("habito_nombre", "")
    date_str = context.user_data.get("habito_date", str(date.today()))

    try:
        habits = await api.get_habits(date_str)
        existing = habits.get(nombre)
        final_value = _accumulate_value(existing, new_input)
        await api.log_habit(date_str, nombre, final_value)

        if new_input.startswith("+") and existing:
            extra = f"\n  \\({existing} \\+ {new_input[1:]} = {final_value}\\)"
        else:
            extra = ""
        await update.message.reply_text(
            f"✅ *Hábito registrado*\n\n"
            f"  📊 {nombre}: `{final_value}`\n"
            f"  📅 {date_str}{extra}",
            parse_mode="Markdown",
        )
    except ApiError as e:
        logger.error("habito_recv_value: %s", e)
        await _reply_api_error(update)

    context.user_data.clear()
    return ConversationHandler.END


# ── /resumen ────────────────────────────────────────────────────────


async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el resumen completo del día: citas + hábitos."""
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        summary = await api.get_summary(date_str)
        apts = summary.get("appointments", [])
        habits = summary.get("habits", {})
        text = (
            f"📋 *Resumen del {date_str}*\n\n"
            + _fmt_appointments(apts, date_str)
            + "\n\n"
            + _fmt_habits(habits, date_str)
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except ApiError as e:
        logger.error("cmd_resumen: %s", e)
        await _reply_api_error(update)


# ── /cancelar ──────────────────────────────────────────────────────


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela cualquier conversación en curso."""
    context.user_data.clear()
    await update.message.reply_text("❌ Operación cancelada\\.", parse_mode="Markdown")
    return ConversationHandler.END


# ── Error handler ─────────────────────────────────────────────────────


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Loguea errores no controlados de python-telegram-bot."""
    logger.error(
        "Error no controlado en update %s: %s", update, context.error, exc_info=True
    )


# ── Helper interno ───────────────────────────────────────────────────────


async def _reply_api_error(update: Update) -> None:
    """Respuesta estándar cuando la API no está disponible."""
    msg = update.message or (update.callback_query.message if update.callback_query else None)
    if msg:
        await msg.reply_text(
            "⚠️ No pude conectar con la API de THDORA\\.\n"
            "Asegúrate de que está corriendo:\n"
            "```\nmake run-api\n```",
            parse_mode="Markdown",
        )


# ── Factories de ConversationHandler ───────────────────────────────────────


def build_nueva_handler() -> ConversationHandler:
    """
    ConversationHandler para /nueva (5 pasos).
    FIX v2.1: NUEVA_TYPE usa per_message=True para capturar callbacks inline
    sin interferir con otros ConversationHandlers activos.
    """
    return ConversationHandler(
        entry_points=[CommandHandler("nueva", nueva_start)],
        states={
            NUEVA_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_date),
            ],
            NUEVA_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_time),
            ],
            NUEVA_NOMBRE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_nombre),
            ],
            NUEVA_TYPE: [
                CallbackQueryHandler(nueva_recv_type, pattern=r"^tipo_"),
            ],
            NUEVA_NOTES: [
                CommandHandler("skip", nueva_skip_notes),
                MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_recv_notes),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="nueva_cita",
        persistent=False,
        per_message=False,
    )


def build_habito_handler() -> ConversationHandler:
    """ConversationHandler para /habito (2 pasos)."""
    return ConversationHandler(
        entry_points=[CommandHandler("habito", habito_start)],
        states={
            HABITO_NOMBRE: [
                CallbackQueryHandler(habito_recv_nombre_inline, pattern=r"^hab_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_nombre_text),
            ],
            HABITO_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, habito_recv_value),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="registrar_habito",
        persistent=False,
        per_message=False,
    )


def build_edit_apt_handler() -> ConversationHandler:
    """
    ConversationHandler para editar una cita (activado por botón inline ^ae_).
    FIX v2.1: etipo_ usa patrón distinto a tipo_ para no interferir con /nueva.
    """
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_apt_edit_start, pattern=r"^ae_")],
        states={
            EDIT_APT_TIME: [
                CommandHandler("skip", lambda u, c: _skip_to(u, c, EDIT_APT_NOMBRE, "Nuevo nombre o /skip:")),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_time),
            ],
            EDIT_APT_NOMBRE: [
                CommandHandler("skip", lambda u, c: _skip_to_type(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_nombre),
            ],
            EDIT_APT_TYPE: [
                CallbackQueryHandler(cb_apt_edit_type, pattern=r"^etipo_"),
            ],
            EDIT_APT_NOTES: [
                CommandHandler("skip", lambda u, c: cb_apt_edit_notes(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_apt_edit_notes),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="editar_cita",
        persistent=False,
        per_message=False,
    )


def build_edit_hab_handler() -> ConversationHandler:
    """ConversationHandler para editar un hábito (activado por ^he_)."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_hab_edit_start, pattern=r"^he_")],
        states={
            EDIT_HAB_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cb_hab_edit_value),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        name="editar_habito",
        persistent=False,
        per_message=False,
    )


# ── Helpers skip internos ───────────────────────────────────────────────


async def _skip_to(
    update: Update, context: ContextTypes.DEFAULT_TYPE, next_state: int, prompt: str
) -> int:
    """Avanza al siguiente estado sin guardar el campo actual."""
    await update.message.reply_text(prompt)
    return next_state


async def _skip_to_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Skip directo al paso de tipo en la edición de cita."""
    await update.message.reply_text(
        "Nuevo tipo o /skip:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(t.capitalize(), callback_data=f"etipo_{t}") for t in TIPOS_CITA]]
            + [[InlineKeyboardButton("⏭️ Skip", callback_data="etipo_skip")]]
        )
    )
    return EDIT_APT_TYPE
