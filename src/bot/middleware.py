"""
Middleware de autorización — Sprint 5.
Lee allowed_users desde DB con cache TTL 60s.
Antes usaba lista estática de .env — ahora 100% desde base de datos.
"""
from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from src.db.session import get_db
from src.db.models import AllowedUser

logger = logging.getLogger(__name__)

_CACHE: dict[str, Any] = {"users": set(), "ts": 0.0}
_CACHE_TTL = 60


def _get_allowed_users() -> set[int]:
    now = time.monotonic()
    if now - _CACHE["ts"] < _CACHE_TTL and _CACHE["users"]:
        return _CACHE["users"]
    try:
        with get_db() as db:
            rows = db.query(AllowedUser.user_id).all()
            _CACHE["users"] = {row[0] for row in rows}
            _CACHE["ts"] = now
            logger.debug("🔄 Cache allowed_users: %d usuarios", len(_CACHE["users"]))
    except Exception as exc:
        logger.error("❌ Error cargando allowed_users desde DB: %s", exc)
    return _CACHE["users"]


def invalidate_allowed_users_cache() -> None:
    """Llamar tras /admin_add_user para forzar refresco inmediato."""
    _CACHE["ts"] = 0.0


def require_allowed_user(func):
    """Decorador: bloquea usuarios no registrados en allowed_users."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        user_id = user.id if user else None
        if not user_id or user_id not in _get_allowed_users():
            logger.warning("⛔️ Acceso denegado a user_id=%s", user_id)
            if update.message:
                await update.message.reply_text(
                    "❌ No tienes permiso para usar THDORA. Contacta al administrador."
                )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
