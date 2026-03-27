"""
Handlers del bot Telegram de THDORA.

Implementa los comandos de gestión de citas y hábitos.
Todos los handlers son async (python-telegram-bot >= 21).

Comandos disponibles::

    /start              → presentación y ayuda
    /citas [YYYY-MM-DD] → ver citas (hoy por defecto)
    /nueva              → crear cita (ConversationHandler, 4 pasos)
    /borrar <id>        → eliminar cita por UUID
    /habitos [YYYY-MM-DD] → ver hábitos (hoy por defecto)
    /habito             → registrar hábito (ConversationHandler, 2 pasos)
    /resumen [YYYY-MM-DD] → resumen completo del día
    /cancelar           → abortar operación en curso

Flujos de conversación::

    /nueva:
        1. Fecha (YYYY-MM-DD o "hoy")
        2. Hora (HH:MM)
        3. Tipo (teclado inline: médica / personal / trabajo / otra)
        4. Notas (texto libre o /skip)

    /habito:
        1. Nombre del hábito (teclado inline + opción libre)
        2. Valor del hábito (texto libre)
"""

import logging
import re
from datetime import date, datetime
from typing import Optional

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

# ── Estados de conversación ────────────────────────────────────────────────────

# /nueva
NUEVA_DATE, NUEVA_TIME, NUEVA_TYPE, NUEVA_NOTES = range(4)

# /habito (rango separado para evitar colisiones)
HABITO_NOMBRE, HABITO_VALUE = range(10, 12)

# ── Constantes de dominio ──────────────────────────────────────────────────────

TIPOS_CITA = ["médica", "personal", "trabajo", "otra"]

HABITOS_COMUNES = [
    "sueno",
    "THC",
    "tabaco",
    "ejercicio",
    "agua",
    "humor",
    "alimentacion",
]

_RE_TIME = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")

# ── Helpers ────────────────────────────────────────────────────────────────────


def _parse_date_arg(arg: Optional[str]) -> str:
    """
    Convierte un argumento de fecha opcional en string YYYY-MM-DD.

    Args:
        arg: String del usuario o None.

    Returns:
        String YYYY-MM-DD — hoy si arg es None o inválido.
    """
    if arg:
        try:
            datetime.strptime(arg, "%Y-%m-%d")
            return arg
        except ValueError:
            pass
    return str(date.today())


def _fmt_appointments(apts: list, date_str: str) -> str:
    """Formatea la lista de citas en markdown de Telegram."""
    if not apts:
        return f"📅 No hay citas el *{date_str}*\\."
    lines = [f"📅 *Citas del {date_str}:*\n"]
    for a in apts:
        notas = f"\n      _{a['notes']}_" if a.get("notes") else ""
        short_id = str(a["id"])[:8]
        lines.append(f"  🕒 `{a['time']}` — {a['type']}{notas}")
        lines.append(f"       🆔 `{short_id}…`\n")
    return "\n".join(lines)


def _fmt_habits(habits: dict, date_str: str) -> str:
    """Formatea el dict de hábitos en markdown de Telegram."""
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


# ── /start ─────────────────────────────────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra la bienvenida y lista de comandos."""
    text = (
        "👋 *Hola, soy THDORA*\n"
        "_Tu asistente personal de gestión de vida_\n\n"
        "*Citas:*\n"
        "  📅 /citas `[YYYY-MM-DD]` — ver citas del día\n"
        "  ➕ /nueva — crear una cita\n"
        "  🗑️ /borrar `<id>` — eliminar una cita\n\n"
        "*Hábitos:*\n"
        "  📊 /habitos `[YYYY-MM-DD]` — ver hábitos\n"
        "  ✏️ /habito — registrar un hábito\n\n"
        "*Resumen:*\n"
        "  📋 /resumen `[YYYY-MM-DD]` — resumen del día\n\n"
        "❌ /cancelar — abortar operación en curso"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ── /citas ─────────────────────────────────────────────────────────────────────


async def cmd_citas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra las citas de un día. Usa hoy por defecto."""
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        apts = await api.get_appointments(date_str)
        await update.message.reply_text(
            _fmt_appointments(apts, date_str), parse_mode="Markdown"
        )
    except ApiError as e:
        logger.error("cmd_citas ApiError: %s", e)
        await _reply_api_error(update)


# ── /nueva — ConversationHandler ───────────────────────────────────────────────


async def nueva_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación para crear una cita."""
    context.user_data.clear()
    await update.message.reply_text(
        "📅 *Nueva cita — paso 1/4*\n\n"
        "¿Para qué fecha? Escribe `YYYY-MM-DD` o simplemente `hoy`\\.",
        parse_mode="Markdown",
    )
    return NUEVA_DATE


async def nueva_recv_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe y valida la fecha."""
    text = update.message.text.strip().lower()
    if text == "hoy":
        date_str = str(date.today())
    else:
        try:
            datetime.strptime(text, "%Y-%m-%d")
            date_str = text
        except ValueError:
            await update.message.reply_text(
                "❌ Formato incorrecto\\. Usa `YYYY-MM-DD` o escribe `hoy`\\.",
                parse_mode="Markdown",
            )
            return NUEVA_DATE

    context.user_data["nueva_date"] = date_str
    await update.message.reply_text(
        f"✅ Fecha: *{date_str}*\n\n"
        "🕒 *Paso 2/4* — ¿A qué hora? \\(formato `HH:MM`, 24h\\)",
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
        f"✅ Hora: *{text}*\n\n📋 *Paso 3/4* — ¿Tipo de cita?",
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
        "📝 *Paso 4/4* — ¿Alguna nota? \\(texto libre o /skip para omitir\\)",
        parse_mode="Markdown",
    )
    return NUEVA_NOTES


async def nueva_recv_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe las notas y guarda la cita."""
    notes = update.message.text.strip()
    return await _save_appointment(update, context, notes)


async def nueva_skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la cita sin notas."""
    return await _save_appointment(update, context, "")


async def _save_appointment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, notes: str
) -> int:
    """Llama a la API para crear la cita y termina la conversación."""
    d = context.user_data.get("nueva_date", str(date.today()))
    t = context.user_data.get("nueva_time", "")
    tp = context.user_data.get("nueva_type", "")

    try:
        result = await api.create_appointment(d, t, tp, notes)
        apt_id = str(result.get("id", ""))
        notas_str = notes or "—"
        await update.message.reply_text(
            f"✅ *Cita creada*\n\n"
            f"  📅 {d}  🕒 {t}\n"
            f"  📋 {tp}\n"
            f"  📝 {notas_str}\n"
            f"  🆔 `{apt_id[:8]}…`",
            parse_mode="Markdown",
        )
    except ApiError as e:
        logger.error("_save_appointment ApiError: %s", e)
        await _reply_api_error(update)

    context.user_data.clear()
    return ConversationHandler.END


# ── /borrar ────────────────────────────────────────────────────────────────────


async def cmd_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Elimina una cita por su UUID (o prefijo de 8 chars del ID)."""
    if not context.args:
        await update.message.reply_text(
            "Uso: /borrar `<id>`\n\nEl ID lo ves con /citas \\(los 8 primeros chars\\)\\.",
            parse_mode="Markdown",
        )
        return

    apt_id = context.args[0]
    try:
        ok = await api.delete_appointment(apt_id)
        if ok:
            await update.message.reply_text(
                f"🗑️ Cita `{apt_id[:8]}…` eliminada\\.", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ No encontré esa cita\\. Verifica el ID con /citas\\.",
                parse_mode="Markdown",
            )
    except ApiError as e:
        logger.error("cmd_borrar ApiError: %s", e)
        await _reply_api_error(update)


# ── /habitos ───────────────────────────────────────────────────────────────────


async def cmd_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra los hábitos de un día. Usa hoy por defecto."""
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        habits = await api.get_habits(date_str)
        await update.message.reply_text(
            _fmt_habits(habits, date_str), parse_mode="Markdown"
        )
    except ApiError as e:
        logger.error("cmd_habitos ApiError: %s", e)
        await _reply_api_error(update)


# ── /habito — ConversationHandler ─────────────────────────────────────────────


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
        await query.edit_message_text(
            "✏️ Escribe el nombre del hábito:",
        )
        return HABITO_NOMBRE

    context.user_data["habito_nombre"] = nombre
    await query.edit_message_text(
        f"✅ Hábito: *{nombre}*\n\n"
        "📊 *Paso 2/2* — ¿Cuál es el valor? \\(ej: `8h`, `0`, `30min`, `2L`\\)",
        parse_mode="Markdown",
    )
    return HABITO_VALUE


async def habito_recv_nombre_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recibe el nombre del hábito como texto libre."""
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío.")
        return HABITO_NOMBRE

    context.user_data["habito_nombre"] = nombre
    await update.message.reply_text(
        f"✅ Hábito: *{nombre}*\n\n"
        "📊 *Paso 2/2* — ¿Cuál es el valor? \\(ej: `8h`, `0`, `30min`, `2L`\\)",
        parse_mode="Markdown",
    )
    return HABITO_VALUE


async def habito_recv_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe el valor del hábito y guarda el registro."""
    value = update.message.text.strip()
    if not value:
        await update.message.reply_text("❌ El valor no puede estar vacío.")
        return HABITO_VALUE

    nombre = context.user_data.get("habito_nombre", "")
    date_str = context.user_data.get("habito_date", str(date.today()))

    try:
        await api.log_habit(date_str, nombre, value)
        await update.message.reply_text(
            f"✅ *Hábito registrado*\n\n"
            f"  📊 {nombre}: `{value}`\n"
            f"  📅 {date_str}",
            parse_mode="Markdown",
        )
    except ApiError as e:
        logger.error("habito_recv_value ApiError: %s", e)
        await _reply_api_error(update)

    context.user_data.clear()
    return ConversationHandler.END


# ── /resumen ───────────────────────────────────────────────────────────────────


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
        logger.error("cmd_resumen ApiError: %s", e)
        await _reply_api_error(update)


# ── /cancelar ──────────────────────────────────────────────────────────────────


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela cualquier conversación en curso."""
    context.user_data.clear()
    await update.message.reply_text("❌ Operación cancelada\\.", parse_mode="Markdown")
    return ConversationHandler.END


# ── Error handler ──────────────────────────────────────────────────────────────


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Loguea errores no controlados de python-telegram-bot."""
    logger.error("Error no controlado en update %s: %s", update, context.error, exc_info=True)


# ── Helpers internos ───────────────────────────────────────────────────────────


async def _reply_api_error(update: Update) -> None:
    """Respuesta estándar cuando la API no está disponible."""
    await update.message.reply_text(
        "⚠️ No pude conectar con la API de THDORA\\.\n"
        "Asegúrate de que está corriendo:\n"
        "```\nmake run-api\n```",
        parse_mode="Markdown",
    )


# ── Factories de ConversationHandler ──────────────────────────────────────────


def build_nueva_handler() -> ConversationHandler:
    """
    Construye el ConversationHandler para /nueva.

    Flujo: fecha → hora → tipo (inline) → notas → guardar.
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
    )


def build_habito_handler() -> ConversationHandler:
    """
    Construye el ConversationHandler para /habito.

    Flujo: nombre del hábito (inline o texto libre) → valor → guardar.
    """
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
    )
