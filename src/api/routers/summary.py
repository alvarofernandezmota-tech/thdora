"""
Router de resumen diario para la API REST de THDORA.

Endpoints:
    GET /summary/{date} → resumen completo del día (citas + hábitos)
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import date as date_type

from src.api.models.summary import DaySummaryResponse
from src.core.impl.json_lifemanager import JsonLifeManager

router = APIRouter(prefix="/summary", tags=["summary"])


def _parse_date(date_str: str) -> date_type:
    try:
        return date_type.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Fecha inválida: '{date_str}'. Usa el formato YYYY-MM-DD.",
        )


@router.get("/{date_str}", response_model=DaySummaryResponse)
def get_day_summary(
    date_str: str,
    manager: JsonLifeManager = Depends(),
) -> DaySummaryResponse:
    """
    Devuelve el resumen completo del día: fecha, citas y hábitos.

    Args:
        date_str: Fecha en formato YYYY-MM-DD.
        manager: Instancia del gestor inyectada.

    Returns:
        DaySummaryResponse: Resumen del día.
    """
    parsed_date = _parse_date(date_str)
    summary = manager.get_day_summary(parsed_date)
    return DaySummaryResponse(**summary)
