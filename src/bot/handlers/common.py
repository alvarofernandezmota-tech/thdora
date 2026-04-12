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
    query = update.callback_query
    await query.answer("Cancelado")
    await query.delete_message()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Error no controlado en update %s: %s", update, context.error, exc_info=True)
