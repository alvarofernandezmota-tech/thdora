"""
Router de configuración de hábitos (F9.2).

Endpoints::

    GET    /habit-config                  → lista toda la configuración
    GET    /habit-config/{name}           → config de un hábito concreto
    POST   /habit-config                  → crear o actualizar config (upsert)
    DELETE /habit-config/{name}           → borrar config de un hábito

Uso:
    La config define el tipo (numeric/time/boolean/text), unidad,
    valores rápidos para el bot y regla de XP para el RPG (F10).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/habit-config", tags=["habit-config"])

VALID_TYPES = ("numeric", "time", "boolean", "text")


# ── Modelos Pydantic ─────────────────────────────────────────────────

class HabitConfigCreate(BaseModel):
    name: str
    habit_type: str = "text"
    unit: Optional[str] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    quick_vals: Optional[List[str]] = None   # ["6h", "7h", "8h"]
    xp_rule: Optional[str] = None            # "gte:7", "any", "eq:0"

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


# ── Endpoints ───────────────────────────────────────────────────────

@router.get("/", response_model=List[HabitConfigResponse])
def list_habit_configs(
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[HabitConfigResponse]:
    """Lista la configuración de todos los hábitos."""
    return manager.get_all_habit_configs()


@router.get("/{name}", response_model=HabitConfigResponse)
def get_habit_config(
    name: str,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> HabitConfigResponse:
    """Devuelve la config de un hábito concreto."""
    cfg = manager.get_habit_config(name)
    if not cfg:
        raise HTTPException(
            status_code=404,
            detail=f"No hay config para el hábito '{name}'.",
        )
    return cfg


@router.post("/", status_code=201, response_model=HabitConfigResponse)
def upsert_habit_config(
    body: HabitConfigCreate,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> HabitConfigResponse:
    """Crea o actualiza la configuración de un hábito (upsert por nombre)."""
    return manager.upsert_habit_config(
        name=body.name,
        habit_type=body.habit_type,
        unit=body.unit,
        min_val=body.min_val,
        max_val=body.max_val,
        quick_vals=body.quick_vals,
        xp_rule=body.xp_rule,
    )


@router.delete("/{name}", status_code=204)
def delete_habit_config(
    name: str,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> None:
    """Borra la configuración de un hábito."""
    deleted = manager.delete_habit_config(name)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"No hay config para el hábito '{name}'.",
        )
