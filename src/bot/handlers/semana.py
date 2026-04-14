"""
Handlers de la vista semanal — /semana y navegación entre semanas.

Optimización de rendimiento (v2):
  - Una sola llamada a get_appointments_week para obtener todas las citas.
  - Las 7 llamadas a get_habits se lanzan en paralelo con asyncio.gather.
  Total: 2 llamadas concurrentes en vez de 14 en serie.
"""

import asyncio
from datetime import date, datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot.api_client import ApiError, ThdoraApiClient
from src.bot.keyboards import _kb_week_nav

api = ThdoraApiClient()

_DAY_NAMES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
_MONTHS    = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]


async def _get_week_habits(monday: date) -> dict:
    """
    Lanza 7 llamadas a get_habits en paralelo.
    Devuelve {date_str: habits_dict_or_empty}.
    """
    async def _safe_habits(d_str: str) -> tuple[str, dict]:
        try:
            h = await api.get_habits(d_str)
            return d_str, h or {}
        except Exception:
            return d_str, {}

    results = await asyncio.gather(*[
        _safe_habits(str(monday + timedelta(days=i)))
        for i in range(7)
    ])
    return dict(results)


async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    monday = str(date.today() - timedelta(days=date.today().weekday()))
    await _show_semana(update.message, monday)


async def _show_semana(msg, monday_str: str) -> None:
    monday = datetime.strptime(monday_str, "%Y-%m-%d").date()
    sunday = monday + timedelta(days=6)
    today  = date.today()

    # 2 llamadas concurrentes en vez de 14 en serie
    week_apts_raw, week_habits = await asyncio.gather(
        _safe_week_apts(monday_str),
        _get_week_habits(monday),
    )

    lines       = [f"📋 *Semana {monday.day} {_MONTHS[monday.month-1]} — {sunday.day} {_MONTHS[sunday.month-1]} {sunday.year}*\n"]
    btn_days    = []
    total_apts  = 0
    days_habits = 0

    for i in range(7):
        d     = monday + timedelta(days=i)
        d_str = str(d)
        dow   = _DAY_NAMES[i]
        mark  = " ◄ hoy" if d == today else ""

        apts   = week_apts_raw.get(d_str, [])
        habits = week_habits.get(d_str, {})

        apt_t = f"📅{len(apts)}"   if apts   else "  —"
        hab_t = f"📊{len(habits)}" if habits else "  —"

        total_apts  += len(apts)
        if habits:
            days_habits += 1

        lines.append(f"  {dow} {d.day:02d}  {apt_t}  {hab_t}{mark}")

        btn_days.append(InlineKeyboardButton(
            f"{dow} {d.day}", callback_data=f"citas_nav_{d_str}"
        ))

    resumen = f"📅 {total_apts} citas  📊 {days_habits} días con hábitos"
    lines.insert(1, resumen)

    nav_kb   = _kb_week_nav(monday_str)
    nav_rows = [list(row) for row in nav_kb.inline_keyboard]
    full_kb  = InlineKeyboardMarkup([btn_days[:4], btn_days[4:]] + nav_rows)

    await msg.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=full_kb)


async def cb_semana_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    monday_str = query.data.replace("semana_nav_", "")
    await _show_semana(query.message, monday_str)


async def _safe_week_apts(monday_str: str) -> dict:
    """Wrapper seguro sobre get_appointments_week. Devuelve {} si falla."""
    try:
        return await api.get_appointments_week(monday_str) or {}
    except Exception:
        return {}
