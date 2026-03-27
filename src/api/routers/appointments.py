"""
Router de citas (appointments) para la API REST de THDORA.

Endpoints::

    POST   /appointments/{date}         → crear cita
    GET    /appointments/{date}         → listar citas del día (con índice)
    DELETE /appointments/{date}/{index} → eliminar por índice 0-based
    PUT    /appointments/{date}/{index} → editar campos de una cita

Diseño:
    Todos los handlers delegan en ``JsonLifeManager`` vía el singleton
    de ``deps.get_manager()``. Los errores de lógica (fecha inválida,
    índice fuera de rango, tipo incorrecto) se traducen a HTTP 422/404.
"""

from datetime import date as date_type
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.deps import get_manager
from src.core.impl.json_lifemanager import JsonLifeManager

router = APIRouter(prefix="/appointments", tags=["appointments"])


# ── Modelos Pydantic ─────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    """Payload para crear una cita."""
    time: str
    name: str = ""
    type: str
    notes: str = ""


class AppointmentUpdate(BaseModel):
    """Payload para actualizar parcialmente una cita. Todos los campos son opcionales."""
    time: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Cita completa con su índice 0-based en la lista del día."""
    index: int
    id: str
    time: str
    name: str
    type: str
    notes: str


class AppointmentCreatedResponse(BaseModel):
    """Respuesta tras crear una cita."""
    id: str
    index: int


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

@router.post("/{date_str}", response_model=AppointmentCreatedResponse, status_code=201)
def create_appointment(
    date_str: str,
    body: AppointmentCreate,
    manager: JsonLifeManager = Depends(get_manager),
) -> AppointmentCreatedResponse:
    """
    Crea una nueva cita para el día indicado.

    Devuelve el UUID generado y el índice 0-based de la nueva cita.
    """
    parsed_date = _parse_date(date_str)
    try:
        apt_id = manager.create_appointment(
            parsed_date, body.time, body.type, body.notes
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Calcular índice de la cita recién creada (la última del día)
    apts = manager.get_appointments(parsed_date)
    index = len(apts) - 1
    return AppointmentCreatedResponse(id=str(apt_id), index=index)


@router.get("/{date_str}", response_model=List[AppointmentResponse])
def get_appointments(
    date_str: str,
    manager: JsonLifeManager = Depends(get_manager),
) -> List[AppointmentResponse]:
    """Lista las citas del día con su índice 0-based."""
    parsed_date = _parse_date(date_str)
    appointments = manager.get_appointments(parsed_date)
    return [
        AppointmentResponse(
            index=i,
            id=apt.get("id", ""),
            time=apt.get("time", ""),
            name=apt.get("name", ""),
            type=apt.get("type", ""),
            notes=apt.get("notes", ""),
        )
        for i, apt in enumerate(appointments)
    ]


@router.delete("/{date_str}/{index}", status_code=204)
def delete_appointment(
    date_str: str,
    index: int,
    manager: JsonLifeManager = Depends(get_manager),
) -> None:
    """Elimina la cita en la posición index del día."""
    parsed_date = _parse_date(date_str)
    try:
        manager.delete_appointment(parsed_date, index)
    except IndexError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/{date_str}/{index}", response_model=AppointmentResponse)
def update_appointment(
    date_str: str,
    index: int,
    body: AppointmentUpdate,
    manager: JsonLifeManager = Depends(get_manager),
) -> AppointmentResponse:
    """
    Actualiza parcialmente una cita existente.

    Solo se modifican los campos presentes en el body (los None se ignoran).
    Devuelve la cita completa actualizada.
    """
    parsed_date = _parse_date(date_str)
    date_str_key = str(parsed_date)

    appointments = manager.get_appointments(parsed_date)
    if index < 0 or index >= len(appointments):
        raise HTTPException(
            status_code=404,
            detail=f"Índice {index} fuera de rango para {date_str_key} "
                   f"(hay {len(appointments)} cita(s))",
        )

    apt = appointments[index]
    if body.time is not None:
        apt["time"] = body.time
    if body.name is not None:
        apt["name"] = body.name
    if body.type is not None:
        try:
            # Reutilizamos la validación del manager
            from src.core.impl.memory_lifemanager import VALID_TYPES
            if body.type not in VALID_TYPES:
                raise HTTPException(
                    status_code=422,
                    detail=f"Tipo inválido: '{body.type}'. Permitidos: {sorted(VALID_TYPES)}",
                )
        except ImportError:
            pass
        apt["type"] = body.type
    if body.notes is not None:
        apt["notes"] = body.notes

    # Persistir directamente en el dict interno y guardar
    manager._data["appointments"][date_str_key][index] = apt
    manager._save()

    return AppointmentResponse(
        index=index,
        id=apt.get("id", ""),
        time=apt.get("time", ""),
        name=apt.get("name", ""),
        type=apt.get("type", ""),
        notes=apt.get("notes", ""),
    )
