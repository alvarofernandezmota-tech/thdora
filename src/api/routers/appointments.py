"""
Router de citas — v3 (multi-user isolation).

Todos los endpoints requieren `telegram_user_id` como query param obligatorio.
Devuelven 400 si falta o es 0.

Endpoints::

    POST   /appointments/{date}                     → crear cita
    GET    /appointments/{date}                     → citas del día
    GET    /appointments/{date}/conflict/{time}     → conflicto de hora
    DELETE /appointments/{date}/{index}             → borrar por índice
    PUT    /appointments/{date}/{index}             → editar cita
    GET    /appointments/range/{from}/{to}          → citas en rango
    GET    /appointments/upcoming/{from}            → próximas citas
    GET    /appointments/week/{date}                → citas de la semana
"""

from datetime import date as date_type, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/appointments", tags=["appointments"])

_DEFAULT_DURATION_MIN = 60


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    time: str
    name: str = ""
    type: str
    notes: str = ""


class AppointmentUpdate(BaseModel):
    time: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    date: str
    time: str
    name: str
    type: str
    notes: Optional[str]
    index: int


class AppointmentCreatedResponse(BaseModel):
    id: int
    index: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(date_str: str) -> str:
    try:
        date_type.fromisoformat(date_str)
        return date_str
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Fecha inválida: '{date_str}'. Usa YYYY-MM-DD.")


def _require_uid(telegram_user_id: int) -> int:
    if not telegram_user_id or telegram_user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="telegram_user_id es obligatorio y debe ser > 0.",
        )
    return telegram_user_id


def _week_bounds(date_str: str) -> tuple[str, str]:
    d = date_type.fromisoformat(date_str)
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return str(monday), str(sunday)


def _to_response(apt: dict) -> AppointmentResponse:
    return AppointmentResponse(
        id=apt["id"], date=apt["date"], time=apt["time"],
        name=apt.get("name", ""), type=apt.get("type", "otra"),
        notes=apt.get("notes"), index=apt["index"],
    )


def _time_to_minutes(time_str: str) -> int:
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


def _find_overlap(
    apts: list, new_time: str, duration: int = _DEFAULT_DURATION_MIN
) -> Optional[dict]:
    new_start = _time_to_minutes(new_time)
    new_end = new_start + duration
    for apt in apts:
        exist_start = _time_to_minutes(apt["time"])
        exist_end = exist_start + duration
        if new_start < exist_end and new_end > exist_start:
            return apt
    return None


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/{date_str}", response_model=AppointmentCreatedResponse, status_code=201)
def create_appointment(
    date_str: str,
    body: AppointmentCreate,
    telegram_user_id: int = Query(..., gt=0, description="Telegram user ID del propietario"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> AppointmentCreatedResponse:
    """Crea una nueva cita para el usuario indicado."""
    _parse_date(date_str)
    _require_uid(telegram_user_id)
    try:
        apt = manager.create_appointment(
            date_str, body.time, body.type, body.notes, body.name,
            user_id=telegram_user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return AppointmentCreatedResponse(id=apt["id"], index=apt["index"])


@router.get("/week/{date_str}", response_model=Dict[str, List[AppointmentResponse]])
def get_appointments_week(
    date_str: str,
    telegram_user_id: int = Query(..., gt=0),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> Dict[str, List[AppointmentResponse]]:
    """Citas de la semana (lun–dom) del usuario."""
    _parse_date(date_str)
    _require_uid(telegram_user_id)
    monday, sunday = _week_bounds(date_str)
    rows = manager.get_appointments_range(monday, sunday, user_id=telegram_user_id)
    result: Dict[str, List[AppointmentResponse]] = {}
    for apt in rows:
        result.setdefault(apt["date"], []).append(_to_response(apt))
    return result


@router.get("/range/{date_from}/{date_to}", response_model=Dict[str, List[AppointmentResponse]])
def get_appointments_range(
    date_from: str,
    date_to: str,
    telegram_user_id: int = Query(..., gt=0),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> Dict[str, List[AppointmentResponse]]:
    """Citas en rango de fechas del usuario."""
    _parse_date(date_from)
    _parse_date(date_to)
    _require_uid(telegram_user_id)
    rows = manager.get_appointments_range(date_from, date_to, user_id=telegram_user_id)
    result: Dict[str, List[AppointmentResponse]] = {}
    for apt in rows:
        result.setdefault(apt["date"], []).append(_to_response(apt))
    return result


@router.get("/upcoming/{date_from}", response_model=List[AppointmentResponse])
def get_upcoming(
    date_from: str,
    telegram_user_id: int = Query(..., gt=0),
    limit: int = Query(default=10, ge=1, le=50),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[AppointmentResponse]:
    """Próximas citas del usuario desde date_from."""
    _parse_date(date_from)
    _require_uid(telegram_user_id)
    rows = manager.get_upcoming_appointments(date_from, limit, user_id=telegram_user_id)
    return [_to_response(apt) for apt in rows]


@router.get("/{date_str}/conflict/{time_str}", response_model=Optional[AppointmentResponse])
def check_conflict(
    date_str: str,
    time_str: str,
    telegram_user_id: int = Query(..., gt=0),
    duration: int = Query(default=_DEFAULT_DURATION_MIN, ge=1, le=480),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> Optional[AppointmentResponse]:
    """Comprueba solapamiento real (60min) para el usuario."""
    _parse_date(date_str)
    _require_uid(telegram_user_id)
    apts = manager.get_appointments(date_str, user_id=telegram_user_id)
    overlap = _find_overlap(apts, time_str, duration)
    if overlap:
        return _to_response(overlap)
    raise HTTPException(status_code=404, detail="Franja libre.")


@router.get("/{date_str}", response_model=List[AppointmentResponse])
def get_appointments(
    date_str: str,
    telegram_user_id: int = Query(..., gt=0),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[AppointmentResponse]:
    """Citas del día del usuario."""
    _parse_date(date_str)
    _require_uid(telegram_user_id)
    return [_to_response(apt) for apt in manager.get_appointments(date_str, user_id=telegram_user_id)]


@router.delete("/{date_str}/{index}", status_code=204)
def delete_appointment(
    date_str: str,
    index: int,
    telegram_user_id: int = Query(..., gt=0),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> None:
    """Borra la cita del usuario con ese índice ordinal."""
    _parse_date(date_str)
    _require_uid(telegram_user_id)
    deleted = manager.delete_appointment(date_str, index, user_id=telegram_user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Cita índice {index} no encontrada el {date_str}.")


@router.put("/{date_str}/{index}", response_model=AppointmentResponse)
def update_appointment(
    date_str: str,
    index: int,
    body: AppointmentUpdate,
    telegram_user_id: int = Query(..., gt=0),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> AppointmentResponse:
    """Edita campos de la cita del usuario."""
    _parse_date(date_str)
    _require_uid(telegram_user_id)
    try:
        updated = manager.update_appointment(
            date_str, index,
            time=body.time, name=body.name,
            apt_type=body.type, notes=body.notes,
            user_id=telegram_user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Cita índice {index} no encontrada el {date_str}.")
    return _to_response(updated)
