"""Decoradores de seguridad para handlers del bot."""
from __future__ import annotations

import functools
import logging
from collections.abc import Callable

from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings

logger = logging.getLogger(__name__)


def _allowed_ids() -> set[int]:
    """Parsea ALLOWED_USERS del entorno y devuelve un set de Telegram user_ids."""
    raw = settings.ALLOWED_USERS.strip()
    if not raw:
        return set()
    return {int(u.strip()) for u in raw.split(",") if u.strip().isdigit()}


def require_allowed_user(func: Callable) -> Callable:
    """Decorador que rechaza el handler si el usuario no está en ALLOWED_USERS.

    Si ALLOWED_USERS está vacío, permite a todos (modo desarrollo).
    En producción siempre debe tener al menos un ID configurado.
    """

    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        allowed = _allowed_ids()
        if not allowed:
            return await func(update, context, *args, **kwargs)
        user_id = update.effective_user.id if update.effective_user else 0
        if user_id not in allowed:
            logger.warning(
                "Acceso denegado | user_id=%s | handler=%s", user_id, func.__name__
            )
            await update.effective_message.reply_text("\u26d4 No tienes acceso a este bot.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapper
