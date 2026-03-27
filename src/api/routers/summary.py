"""
Router de resumen diario — v2 con SQLiteLifeManager.

Endpoints::

    GET /summary/{date}          → resumen del día (citas + hábitos)
    GET /summary/week/{date}     → resumen de la semana
"""

from datetime import date as date_type, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/summary", tags=["summary"])


def _parse_date(date_str: str) -> str:
    try:
        date_type.fromisoformat(date_str)
        return date_str
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Fecha inválida: '{date_str}'.")


@router.get("/{date_str}")
def get_summary(
    date_str: str,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> Dict[str, Any]:
    """Resumen completo del día: citas + hábitos."""
    _parse_date(date_str)
    return manager.get_summary(date_str)


@router.get("/week/{date_str}")
def get_summary_week(
    date_str: str,
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[Dict[str, Any]]:
    """Resumen de cada día de la semana que contiene date_str."""
    _parse_date(date_str)
    d = date_type.fromisoformat(date_str)
    monday = d - timedelta(days=d.weekday())
    result = []
    for i in range(7):
        day = str(monday + timedelta(days=i))
        result.append(manager.get_summary(day))
    return result
