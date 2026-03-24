"""
Router de citas (appointments) para la API REST de THDORA.

Endpoints:
    POST   /appointments/{date}         → crear cita
    GET    /appointments/{date}         → listar citas del día
    DELETE /appointments/{date}/{index} → eliminar cita por índice
"""

from datetime import date as date_type
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.api.models.appointment import (
    AppointmentCreate,
    AppointmentCreatedResponse,
    AppointmentResponse,
)
from src.core.impl.json_lifemanager import JsonLifeManager

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _parse_date(date_str: str) -> date_type:
    """Parsea un string ISO a date, lanzando HTTP 422 si el formato es inválido."""
    try:
        return date_type.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Fecha inválida: '{date_str}'. Usa el formato YYYY-MM-DD.",
        )


@router.post("/{date_str}", response_model=AppointmentCreatedResponse, status_code=201)
def create_appointment(
    date_str: str,
    body: AppointmentCreate,
    manager: JsonLifeManager = Depends(),
) -> AppointmentCreatedResponse:
    """
    Crea una nueva cita para el día indicado.

    Args:
        date_str: Fecha en formato YYYY-MM-DD.
        body: Datos de la cita (time, type, notes).
        manager: Instancia del gestor inyectada por FastAPI.

    Returns:
        AppointmentCreatedResponse: UUID de la cita creada.

    Raises:
        HTTPException 422: Si la fecha, hora o tipo son inválidos.
    """
    parsed_date = _parse_date(date_str)
    try:
        apt_id = manager.create_appointment(
            parsed_date, body.time, body.type, body.notes
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return AppointmentCreatedResponse(id=str(apt_id))


@router.get("/{date_str}", response_model=List[AppointmentResponse])
def get_appointments(
    date_str: str,
    manager: JsonLifeManager = Depends(),
) -> List[AppointmentResponse]:
    """
    Devuelve todas las citas de un día.

    Args:
        date_str: Fecha en formato YYYY-MM-DD.
        manager: Instancia del gestor inyectada por FastAPI.

    Returns:
        List[AppointmentResponse]: Lista de citas del día (vacía si no hay ninguna).

    Raises:
        HTTPException 422: Si el formato de fecha es inválido.
    """
    parsed_date = _parse_date(date_str)
    appointments = manager.get_appointments(parsed_date)
    return [AppointmentResponse(**apt) for apt in appointments]


@router.delete("/{date_str}/{index}", status_code=204)
def delete_appointment(
    date_str: str,
    index: int,
    manager: JsonLifeManager = Depends(),
) -> None:
    """
    Elimina la cita en el índice indicado para el día dado.

    Args:
        date_str: Fecha en formato YYYY-MM-DD.
        index: Posición 0-based de la cita en la lista del día.
        manager: Instancia del gestor inyectada por FastAPI.

    Raises:
        HTTPException 422: Si el formato de fecha es inválido.
        HTTPException 404: Si el índice no corresponde a ninguna cita.
    """
    parsed_date = _parse_date(date_str)
    try:
        manager.delete_appointment(parsed_date, index)
    except IndexError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
