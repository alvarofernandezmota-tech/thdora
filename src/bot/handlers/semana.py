"""
Handlers de la vista semanal — /semana y navegación entre semanas.
"""

from datetime import date, datetime, timedelta

from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.bot.api_client import ApiError, ThdoraApiClient
from src.bot.keyboards import _kb_week_nav
from src.bot.utils.dates import _monday

api = ThdoraApiClient()


async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    monday = str(date.today() - timedelta(days=date.today().weekday()))
    await _show_semana(update.message, monday)


async def _show_semana(msg, monday_str: str) -> None:
    monday    = datetime.strptime(monday_str, "%Y-%m-%d").date()
    sunday    = monday + timedelta(days=6)
    today     = date.today()
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    months    = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

    lines        = [f"📋 *Semana {monday.day} {months[monday.month-1]} — {sunday.day} {months[sunday.month-1]} {sunday.year}*\n"]
    btn_days     = []
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
            if habits:
                days_habits += 1
            lines.append(f"  {dow} {d.day:02d}  {apt_t}  {hab_t}{mark}")
        except ApiError:
            lines.append(f"  {dow} {d.day:02d}  ⚠️{mark}")
        btn_days.append(InlineKeyboardButton(
            f"{dow} {d.day}", callback_data=f"citas_nav_{d_str}"
        ))

    resumen = f"📅 {total_apts} citas  📊 {days_habits} días con hábitos"
    lines.insert(1, resumen)

    nav_kb   = _kb_week_nav(monday_str)
    nav_rows = [list(row) for row in nav_kb.inline_keyboard]
    from telegram import InlineKeyboardMarkup
    full_kb  = InlineKeyboardMarkup([btn_days[:4], btn_days[4:]] + nav_rows)
    await msg.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=full_kb)


async def cb_semana_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    monday_str = query.data.replace("semana_nav_", "")
    await _show_semana(query.message, monday_str)
