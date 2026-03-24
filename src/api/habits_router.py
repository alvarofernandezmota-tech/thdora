"""
Router de hábitos (habits) para la API REST de THDORA.

Endpoints:
    POST /habits/{date}  → registrar hábito del día
    GET  /habits/{date}  → obtener hábitos del día
"""

from datetime import date as date_type
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException

from src.api.models.habit import HabitCreate, HabitResponse
from src.core.impl.json_lifemanager import JsonLifeManager

router = APIRouter(prefix="/habits", tags=["habits"])


def _parse_date(date_str: str) -> date_type:
    """Parsea un string ISO a date, lanzando HTTP 422 si el formato es inválido."""
    try:
        return date_type.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Fecha inválida: '{date_str}'. Usa el formato YYYY-MM-DD.",
        )


@router.post("/{date_str}", status_code=201)
def log_habit(
    date_str: str,
    body: HabitCreate,
    manager: JsonLifeManager = Depends(),
) -> Dict[str, str]:
    """
    Registra o actualiza un hábito para el día indicado.

    Args:
        date_str: Fecha en formato YYYY-MM-DD.
        body: Datos del hábito (habit, value).
        manager: Instancia del gestor inyectada por FastAPI.

    Returns:
        Dict: Confirmación con el hábito y valor registrados.

    Raises:
        HTTPException 422: Si el formato de fecha es inválido.
    """
    parsed_date = _parse_date(date_str)
    manager.log_habit(parsed_date, body.habit, body.value)
    return {"habit": body.habit, "value": body.value}


@router.get("/{date_str}", response_model=List[HabitResponse])
def get_habits(
    date_str: str,
    manager: JsonLifeManager = Depends(),
) -> List[HabitResponse]:
    """
    Devuelve todos los hábitos registrados para un día.

    Args:
        date_str: Fecha en formato YYYY-MM-DD.
        manager: Instancia del gestor inyectada por FastAPI.

    Returns:
        List[HabitResponse]: Lista de hábitos del día (vacía si no hay ninguno).

    Raises:
        HTTPException 422: Si el formato de fecha es inválido.
    """
    parsed_date = _parse_date(date_str)
    habits = manager.get_habits(parsed_date)
    return [HabitResponse(habit=k, value=v) for k, v in habits.items()]
