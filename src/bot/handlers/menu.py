"""
Handlers del menú principal — /start, 🏠 Menú.

Notas:
    - quick_nueva_* y quick_habito_* son capturados por los ConversationHandlers
      de citas.py y habitos.py respectivamente.
    - quick_config es entry_point de build_config_handler() en config.py.
      NO se registra como handler global para evitar conflicto con el
      ConversationHandler; cb_quick_config ya no existe en este módulo.
    - cmd_start programa los jobs diarios del scheduler para el usuario
      (daily_summary y evening_log) si tiene config guardada.
"""

import logging
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.api_client import ThdoraApiClient
from src.bot.keyboards import _kb_start
from src.bot.scheduler import schedule_user_jobs
from src.bot.utils.dates import _date_short, _greeting

logger = logging.getLogger(__name__)
api    = ThdoraApiClient()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra el menú principal y programa los jobs diarios del scheduler.
    Se llama al arrancar el bot (/start) y es el único punto donde se
    garantiza que los jobs diarios quedan activos para ese usuario.
    """
    today      = str(date.today())
    greeting   = _greeting()
    date_short = _date_short(today)
    user_id    = str(update.effective_user.id)

    try:
        apts_hoy  = await api.get_appointments(today)
        n         = len(apts_hoy)
        citas_txt = f"\n⏰ Tienes *{n} cita{'s' if n != 1 else ''}* hoy" if n else ""
    except Exception:
        citas_txt = ""

    # Programar jobs diarios del scheduler para este usuario
    try:
        cfg = await api.get_user_config(user_id)
        schedule_user_jobs(update.get_bot(), user_id, cfg)
    except Exception as e:
        logger.warning("No se pudieron programar jobs para %s: %s", user_id, e)

    await update.message.reply_text(
        f"{greeting}, soy *THDORA* — {date_short}{citas_txt}\n"
        f"_Tu asistente personal de gestión de vida_",
        parse_mode="Markdown",
        reply_markup=_kb_start(),
    )


async def cb_menu_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vuelve al menú principal desde cualquier botón 🏠 Menú."""
    query      = update.callback_query
    await query.answer()
    today      = str(date.today())
    greeting   = _greeting()
    date_short = _date_short(today)
    try:
        apts_hoy  = await api.get_appointments(today)
        n         = len(apts_hoy)
        citas_txt = f"\n⏰ Tienes *{n} cita{'s' if n != 1 else ''}* hoy" if n else ""
    except Exception:
        citas_txt = ""
    await query.message.reply_text(
        f"{greeting}, soy *THDORA* — {date_short}{citas_txt}",
        parse_mode="Markdown",
        reply_markup=_kb_start(),
    )
