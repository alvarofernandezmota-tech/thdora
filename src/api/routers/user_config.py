"""
Router de configuración de usuario — F12 Notificaciones.

Endpoints::

    GET  /user_config/{user_id}   → devuelve config (crea con defaults si no existe)
    PUT  /user_config/{user_id}   → actualiza campos enviados (patch semántico)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/user_config", tags=["user_config"])


# ── Schemas ────────────────────────────────────────────────

class UserConfigUpdate(BaseModel):
    """Todos los campos opcionales — solo se actualizan los enviados."""
    daily_summary_enabled: bool | None = None
    daily_summary_time: str | None = None      # HH:MM
    notif_enabled: bool | None = None
    notif_offsets: list[str] | None = None     # ["60", "30", "15"]
    notif_ask_confirm: bool | None = None
    evening_log_enabled: bool | None = None
    evening_log_time: str | None = None        # HH:MM
    timezone: str | None = None


# ── Endpoints ───────────────────────────────────────────────

@router.get("/{user_id}")
def get_user_config(
    user_id: str,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> dict:
    """
    Devuelve la configuración del usuario.
    Si no existe, la crea con los valores predeterminados automáticamente.
    Nunca devuelve 404 — el usuario siempre tiene configuración.
    """
    return manager.get_user_config(user_id)


@router.put("/{user_id}")
def update_user_config(
    user_id: str,
    body: UserConfigUpdate,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> dict:
    """
    Actualiza la configuración del usuario.
    Solo modifica los campos enviados en el body (semántica PATCH sobre PUT).
    Si el usuario no tiene fila todavía, la crea con defaults primero.
    """
    return manager.upsert_user_config(
        user_id=user_id,
        daily_summary_enabled=body.daily_summary_enabled,
        daily_summary_time=body.daily_summary_time,
        notif_enabled=body.notif_enabled,
        notif_offsets=body.notif_offsets,
        notif_ask_confirm=body.notif_ask_confirm,
        evening_log_enabled=body.evening_log_enabled,
        evening_log_time=body.evening_log_time,
        timezone=body.timezone,
    )
