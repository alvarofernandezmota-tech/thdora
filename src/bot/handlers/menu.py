"""
Handlers del menú principal — /start, 🏠 Menú.
Los botones quick_nueva y quick_habito ahora son capturados
directamente por los ConversationHandlers de citas.py y habitos.py.
"""

from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.keyboards import _kb_start
from src.bot.utils.dates import _date_short, _greeting

api = ThdoraApiClient()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    today      = str(date.today())
    greeting   = _greeting()
    date_short = _date_short(today)
    try:
        apts_hoy = await api.get_appointments(today)
        n        = len(apts_hoy)
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
    query      = update.callback_query
    await query.answer()
    today      = str(date.today())
    greeting   = _greeting()
    date_short = _date_short(today)
    try:
        apts_hoy = await api.get_appointments(today)
        n        = len(apts_hoy)
        citas_txt = f"\n⏰ Tienes *{n} cita{'s' if n != 1 else ''}* hoy" if n else ""
    except Exception:
        citas_txt = ""
    await query.message.reply_text(
        f"{greeting}, soy *THDORA* — {date_short}{citas_txt}",
        parse_mode="Markdown",
        reply_markup=_kb_start(),
    )


async def cb_quick_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botón ⚙️ Config del menú — informa al usuario que use /config."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("⚙️ Usa /config para gestionar los tipos de hábitos.")
