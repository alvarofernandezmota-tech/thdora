"""
Router de configuración de hábitos (multi-user).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/habit-config", tags=["habit-config"])

VALID_TYPES = ("numeric", "time", "boolean", "text")


class HabitConfigCreate(BaseModel):
    name: str
    habit_type: str = "text"
    unit: Optional[str] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    quick_vals: Optional[List[str]] = None
    xp_rule: Optional[str] = None

    @field_validator("habit_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"habit_type debe ser uno de: {VALID_TYPES}")
        return v


class HabitConfigResponse(BaseModel):
    id: int
    name: str
    habit_type: str
    unit: Optional[str]
    min_val: Optional[float]
    max_val: Optional[float]
    quick_vals: List[str]
    xp_rule: Optional[str]


@router.get("/", response_model=List[HabitConfigResponse])
def list_habit_configs(
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[HabitConfigResponse]:
    return manager.get_all_habit_configs(user_id=user_id)


@router.get("/{name}", response_model=HabitConfigResponse)
def get_habit_config(
    name: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> HabitConfigResponse:
    cfg = manager.get_habit_config(name, user_id=user_id)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"No hay config para el hábito '{name}'.")
    return cfg


@router.post("/", status_code=201, response_model=HabitConfigResponse)
def upsert_habit_config(
    body: HabitConfigCreate,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> HabitConfigResponse:
    return manager.upsert_habit_config(
        name=body.name, habit_type=body.habit_type, unit=body.unit,
        min_val=body.min_val, max_val=body.max_val, quick_vals=body.quick_vals,
        xp_rule=body.xp_rule, user_id=user_id,
    )


@router.delete("/{name}", status_code=204)
def delete_habit_config(
    name: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> None:
    deleted = manager.delete_habit_config(name, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"No hay config para el hábito '{name}'.")
