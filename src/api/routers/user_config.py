"""
Router de configuración de usuario — multi-user.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/user_config", tags=["user_config"])


class UserConfigUpdate(BaseModel):
    daily_summary_enabled: bool | None = None
    daily_summary_time: str | None = None
    notif_enabled: bool | None = None
    notif_offsets: list[str] | None = None
    notif_ask_confirm: bool | None = None
    evening_log_enabled: bool | None = None
    evening_log_time: str | None = None
    timezone: str | None = None


@router.get("/{user_id}")
def get_user_config(
    user_id: int,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> dict:
    return manager.get_user_config(user_id)


@router.put("/{user_id}")
def update_user_config(
    user_id: int,
    body: UserConfigUpdate,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> dict:
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
