"""Handlers de citas — flujo de mover cita con huecos disponibles."""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot.api_client import ApiClient

logger = logging.getLogger(__name__)

_SLOT_START = time(8, 0)
_SLOT_END = time(21, 30)
_SLOT_MINUTES = 30
_MAX_BUTTONS = 12
_TIGHT_MARGIN_MINUTES = 30


def calculate_free_slots(citas: list[dict], fecha: str) -> list[str]:
    """Calcula huecos libres de 30 min entre 08:00 y 22:00."""
    busy: list[datetime] = []
    ref = datetime.fromisoformat(fecha) if fecha else datetime.today()
    for c in citas:
        try:
            h, m = map(int, c["hora"].split(":"))
            busy.append(ref.replace(hour=h, minute=m, second=0, microsecond=0))
        except (KeyError, ValueError):
            continue
    busy.sort()

    slots: list[str] = []
    current = datetime.combine(ref.date(), _SLOT_START)
    end_limit = datetime.combine(ref.date(), _SLOT_END)

    while current <= end_limit:
        slot_end = current + timedelta(minutes=_SLOT_MINUTES)
        is_busy = any(current <= b < slot_end for b in busy)
        if not is_busy:
            label = current.strftime("%H:%M")
            tight = any(slot_end <= b < slot_end + timedelta(minutes=_TIGHT_MARGIN_MINUTES) for b in busy)
            if tight:
                label = f"⚠️ {label}"
            slots.append(label)
        current += timedelta(minutes=_SLOT_MINUTES)

    return slots


async def show_available_slots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra inline keyboard con huecos disponibles para mover una cita."""
    query = update.callback_query
    if query:
        await query.answer()

    uid = update.effective_user.id if update.effective_user else 0
    cita_id: int = context.user_data.get("cita_id", 0)
    nombre: str = context.user_data.get("cita_nombre", "Cita")
    hora_actual: str = context.user_data.get("cita_hora_actual", "??:??")
    fecha_destino: str = context.user_data.get("fecha_destino", date.today().isoformat())

    api = ApiClient()
    citas_destino: list[dict] = await api.get_appointments(fecha=fecha_destino, user_id=uid)

    raw_slots = calculate_free_slots(citas_destino, fecha_destino)
    slots = raw_slots[:_MAX_BUTTONS]

    if not slots:
        text = f"❌ No hay huecos disponibles el {fecha_destino}."
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    keyboard: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for slot in slots:
        hora_limpia = slot.replace("⚠️ ", "").strip()
        row.append(InlineKeyboardButton(text=slot, callback_data=f"MOVE_{cita_id}_{hora_limpia}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    markup = InlineKeyboardMarkup(keyboard)
    text = f"📅 Elige un hueco para mover *{nombre}* (actualmente {hora_actual}) el {fecha_destino}:"
    if query:
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")


async def handle_move_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa callback MOVE_{cita_id}_{hora_nueva} y muestra confirmación."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_", 2)
    if len(parts) != 3:
        await query.edit_message_text("❌ Error en callback data.")
        return
    _, cita_id_str, hora_nueva = parts
    nombre: str = context.user_data.get("cita_nombre", "Cita")
    hora_actual: str = context.user_data.get("cita_hora_actual", "??:??")
    context.user_data["pending_move"] = {"cita_id": cita_id_str, "hora_nueva": hora_nueva}
    confirm_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Confirmar", callback_data=f"CONFIRM_MOVE_{cita_id_str}_{hora_nueva}"),
        InlineKeyboardButton("❌ Cancelar", callback_data="CANCEL_MOVE"),
    ]])
    msg = f"Mover *{nombre}* de {hora_actual} → {hora_nueva}?\n✅ Confirmar  ❌ Cancelar"
    await query.edit_message_text(msg, reply_markup=confirm_keyboard, parse_mode="Markdown")
