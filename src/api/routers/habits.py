"""
Router de hábitos (habits) para la API REST de THDORA.

Endpoints::

    POST   /habits/{date}          → registrar o sobreescribir hábito
    GET    /habits/{date}          → listar hábitos del día
    DELETE /habits/{date}/{habit}  → eliminar un hábito concreto
    PUT    /habits/{date}/{habit}  → actualizar el valor de un hábito

Diseño:
    Los hábitos se almacenan como Dict[str, str] en el JSON.
    DELETE y PUT operan directamente sobre ese dict y persisten.
    El cálculo de valores acumulativos ('+2L') se hace en el bot
    (handlers.py) antes de llamar a POST — la API siempre recibe
    el valor final ya calculado.
"""

from datetime import date as date_type
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.deps import get_manager
from src.core.impl.json_lifemanager import JsonLifeManager

router = APIRouter(prefix="/habits", tags=["habits"])


# ── Modelos Pydantic ─────────────────────────────────────────────────────────

class HabitCreate(BaseModel):
    """Payload para registrar un hábito."""
    habit: str
    value: str


class HabitUpdate(BaseModel):
    """Payload para actualizar el valor de un hábito existente."""
    value: str


class HabitResponse(BaseModel):
    """Hábito devuelto por GET."""
    habit: str
    value: str


# ── Helper ─────────────────────────────────────────────────────────────

def _parse_date(date_str: str) -> date_type:
    """Parsea YYYY-MM-DD. Lanza HTTP 422 si el formato es inválido."""
    try:
        return date_type.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Fecha inválida: '{date_str}'. Usa el formato YYYY-MM-DD.",
        )


# ── Endpoints ──────────────────────────────────────────────────────────

@router.post("/{date_str}", status_code=201)
def log_habit(
    date_str: str,
    body: HabitCreate,
    manager: JsonLifeManager = Depends(get_manager),
) -> Dict[str, str]:
    """Registra o sobreescribe un hábito del día."""
    parsed_date = _parse_date(date_str)
    manager.log_habit(parsed_date, body.habit, body.value)
    return {"habit": body.habit, "value": body.value}


@router.get("/{date_str}", response_model=List[HabitResponse])
def get_habits(
    date_str: str,
    manager: JsonLifeManager = Depends(get_manager),
) -> List[HabitResponse]:
    """Lista los hábitos del día."""
    parsed_date = _parse_date(date_str)
    habits = manager.get_habits(parsed_date)
    return [HabitResponse(habit=k, value=v) for k, v in habits.items()]


@router.delete("/{date_str}/{habit}", status_code=204)
def delete_habit(
    date_str: str,
    habit: str,
    manager: JsonLifeManager = Depends(get_manager),
) -> None:
    """
    Elimina un hábito concreto del día.

    Raises:
        HTTP 404 si el hábito no existe en ese día.
    """
    parsed_date = _parse_date(date_str)
    date_key = str(parsed_date)
    habits = manager._data.get("habits", {}).get(date_key, {})

    if habit not in habits:
        raise HTTPException(
            status_code=404,
            detail=f"Hábito '{habit}' no encontrado el {date_key}.",
        )

    del manager._data["habits"][date_key][habit]
    manager._save()


@router.put("/{date_str}/{habit}", response_model=HabitResponse)
def update_habit(
    date_str: str,
    habit: str,
    body: HabitUpdate,
    manager: JsonLifeManager = Depends(get_manager),
) -> HabitResponse:
    """
    Actualiza el valor de un hábito existente.

    Raises:
        HTTP 404 si el hábito no existe en ese día.
    """
    parsed_date = _parse_date(date_str)
    date_key = str(parsed_date)
    habits = manager._data.get("habits", {}).get(date_key, {})

    if habit not in habits:
        raise HTTPException(
            status_code=404,
            detail=f"Hábito '{habit}' no encontrado el {date_key}. "
                   f"Usa POST para crearlo.",
        )

    manager._data["habits"][date_key][habit] = body.value
    manager._save()
    return HabitResponse(habit=habit, value=body.value)
