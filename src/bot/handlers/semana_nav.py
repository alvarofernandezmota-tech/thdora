"""Handlers de semana — navegación completa PREV/NEXT/TODAY."""

from __future__ import annotations

import logging
from datetime import date, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot.api_client import ApiClient

logger = logging.getLogger(__name__)

_LOCALE_MONTHS_ES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def get_week_range(offset: int = 0) -> tuple[date, date]:
    """Devuelve (lunes, domingo) de la semana actual ± offset semanas."""
    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _week_center_label(monday: date, sunday: date) -> str:
    """Genera etiqueta 'DD–DD mes' para el botón central de navegación."""
    mes = _LOCALE_MONTHS_ES[sunday.month]
    if monday.month == sunday.month:
        return f"{monday.day}–{sunday.day} {mes}"
    return f"{monday.day} {_LOCALE_MONTHS_ES[monday.month]}–{sunday.day} {mes}"


async def show_week_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra vista semanal con navegación PREV/NEXT/TODAY."""
    query = update.callback_query
    if query:
        await query.answer()
        if query.data == "WEEK_NEXT":
            context.user_data["week_offset"] = context.user_data.get("week_offset", 0) + 1
        elif query.data == "WEEK_PREV":
            context.user_data["week_offset"] = context.user_data.get("week_offset", 0) - 1
        elif query.data == "WEEK_TODAY":
            context.user_data["week_offset"] = 0

    offset: int = context.user_data.get("week_offset", 0)
    monday, sunday = get_week_range(offset)

    uid = update.effective_user.id if update.effective_user else 0
    api = ApiClient()
    citas: list[dict] = await api.get_appointments_range(
        fecha_inicio=monday.isoformat(), fecha_fin=sunday.isoformat(), user_id=uid
    )

    by_day: dict[str, list[dict]] = {}
    for c in citas:
        by_day.setdefault(c.get("fecha", ""), []).append(c)

    day_buttons: list[list[InlineKeyboardButton]] = []
    current, row = monday, []
    while current <= sunday:
        iso = current.isoformat()
        day_citas = by_day.get(iso, [])
        label = f"{current.day}" + (f" ({len(day_citas)})" if day_citas else "")
        row.append(InlineKeyboardButton(label, callback_data=f"DAY_{iso}" if day_citas else f"DAY_EMPTY_{iso}"))
        if len(row) == 7:
            day_buttons.append(row)
            row = []
        current += timedelta(days=1)
    if row:
        day_buttons.append(row)

    center_label = _week_center_label(monday, sunday)
    nav_row = [
        InlineKeyboardButton("◀", callback_data="WEEK_PREV"),
        InlineKeyboardButton(center_label, callback_data="WEEK_TODAY"),
        InlineKeyboardButton("▶", callback_data="WEEK_NEXT"),
    ]
    keyboard = InlineKeyboardMarkup(day_buttons + [nav_row])

    if not citas:
        text = "📭 Semana libre 🎉"
    else:
        lines = [f"📅 Semana {center_label}:"]
        for iso_day in sorted(by_day):
            for c in by_day[iso_day]:
                lines.append(f"⏰ {c.get('hora', '?')} — {c.get('nombre', 'Cita')}")
        text = "\n".join(lines)

    send = query.edit_message_text if query else update.message.reply_text
    await send(text, reply_markup=keyboard)
