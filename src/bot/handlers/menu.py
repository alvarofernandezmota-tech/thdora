"""
Handlers del menú principal — /start, 🏠 Menú, botones rápidos.
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


async def cb_quick_dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botones rápidos desde /start y vistas de día."""
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "quick_nueva" or data.startswith("quick_nueva_"):
        context.user_data.clear()
        if data.startswith("quick_nueva_"):
            fecha = data.replace("quick_nueva_", "")
            context.user_data["nueva_date"] = fecha
        # El ConversationHandler de /nueva se encarga del resto
        # Aquí sólo disparamos el flujo si viene de botón sin fecha
        from src.bot.keyboards import _kb_franjas
        from src.bot.utils.dates import _date_short
        fecha = context.user_data.get("nueva_date", str(date.today()))
        await query.message.reply_text(
            f"📅 *Nueva cita para {_date_short(fecha)}*\n\n"
            f"🕐 *Paso 1* — ¿En qué franja del día?",
            parse_mode="Markdown",
            reply_markup=_kb_franjas(),
        )

    elif data == "quick_habito" or data.startswith("quick_habito_"):
        context.user_data.clear()
        if data.startswith("quick_habito_"):
            fecha = data.replace("quick_habito_", "")
            context.user_data["habito_date"] = fecha
        else:
            context.user_data["habito_date"] = str(date.today())
        from src.bot.utils.dates import _date_short
        fecha_label = _date_short(context.user_data["habito_date"])
        await query.message.reply_text(
            f"📊 *Nuevo hábito para {fecha_label}*\n\n✏️ *Paso 1/2* — ¿Cómo se llama el hábito?",
            parse_mode="Markdown",
        )

    elif data == "quick_config":
        await query.message.reply_text("⚙️ Usa /config para gestionar los tipos de hábitos.")
