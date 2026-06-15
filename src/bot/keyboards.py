# src/bot/keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def _kb_start() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["/citas", "/nueva"],
            ["/habito", "/diario"],
            ["/semana", "/help"]
        ],
        resize_keyboard=True
    )


def kb_confirm(action: str, item: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Sí", callback_data=f"confirm_{action}_{item}")],
        [InlineKeyboardButton("❌ No", callback_data="cancel")]
    ])


def kb_date_selection(dates: list) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(d, callback_data=f"date_{d}")] for d in dates]
    buttons.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)


def kb_time_slots(times: list) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in times]
    buttons.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)
