"""
Handlers comunes: /cancelar, /resumen, error handler.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.api_client import ApiError, ThdoraApiClient
from src.bot.keyboards import _kb_back
from src.bot.utils.dates import _parse_date_arg, _date_label

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()


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


async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el resumen del día: citas + hábitos."""
    date_str = _parse_date_arg(context.args[0] if context.args else None)
    try:
        summary = await api.get_summary(date_str)
        apts    = summary.get("appointments", [])
        habits  = summary.get("habits", {})
        label   = _date_label(date_str)
        text    = (
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
        await update.message.reply_text(
            "⚠️ No pude conectar con la API\\. Asegúrate: `make run-api`",
            parse_mode="Markdown",
        )


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela cualquier flujo activo y vuelve al menú."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Operación cancelada\\.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Menú", callback_data="menu_home")
        ]]),
    )
    return ConversationHandler.END


async def cb_cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botón cancelar en mensajes inline — borra el mensaje."""
    query = update.callback_query
    await query.answer("Cancelado")
    await query.delete_message()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Captura errores no controlados, los loguea e informa al usuario."""
    logger.error("Error no controlado en update %s: %s", update, context.error, exc_info=True)
    # Intentar notificar al usuario si hay update con mensaje o query
    if not isinstance(update, Update):
        return
    text = "⚠️ Algo ha ido mal. Inténtalo de nuevo o usa /cancelar."
    try:
        if update.callback_query:
            await update.callback_query.answer(text, show_alert=True)
        elif update.message:
            await update.message.reply_text(text)
    except Exception:
        pass  # Si falla el envío no hay nada más que hacer
