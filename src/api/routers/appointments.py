"""
Router de citas — v2.3 (multi-user con user_id).
"""

from datetime import date as date_type, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/appointments", tags=["appointments"])

_DEFAULT_DURATION_MIN = 60


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


def _parse_date(date_str: str) -> str:
    try:
        date_type.fromisoformat(date_str)
        return date_str
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Fecha inválida: '{date_str}'. Usa YYYY-MM-DD.")


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


def _find_overlap(apts: list, new_time: str, duration: int = _DEFAULT_DURATION_MIN) -> Optional[dict]:
    new_start = _time_to_minutes(new_time)
    new_end = new_start + duration
    for apt in apts:
        exist_start = _time_to_minutes(apt["time"])
        exist_end = exist_start + duration
        if new_start < exist_end and new_end > exist_start:
            return apt
    return None


@router.post("/{date_str}", response_model=AppointmentCreatedResponse, status_code=201)
def create_appointment(
    date_str: str,
    body: AppointmentCreate,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> AppointmentCreatedResponse:
    _parse_date(date_str)
    try:
        apt = manager.create_appointment(date_str, body.time, body.type, body.notes, body.name, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return AppointmentCreatedResponse(id=apt["id"], index=apt["index"])


@router.get("/week/{date_str}", response_model=Dict[str, List[AppointmentResponse]])
def get_appointments_week(
    date_str: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> Dict[str, List[AppointmentResponse]]:
    _parse_date(date_str)
    monday, sunday = _week_bounds(date_str)
    rows = manager.get_appointments_range(monday, sunday, user_id=user_id)
    result: Dict[str, List[AppointmentResponse]] = {}
    for apt in rows:
        result.setdefault(apt["date"], []).append(_to_response(apt))
    return result


@router.get("/range/{date_from}/{date_to}", response_model=Dict[str, List[AppointmentResponse]])
def get_appointments_range(
    date_from: str,
    date_to: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> Dict[str, List[AppointmentResponse]]:
    _parse_date(date_from)
    _parse_date(date_to)
    rows = manager.get_appointments_range(date_from, date_to, user_id=user_id)
    result: Dict[str, List[AppointmentResponse]] = {}
    for apt in rows:
        result.setdefault(apt["date"], []).append(_to_response(apt))
    return result


@router.get("/upcoming/{date_from}", response_model=List[AppointmentResponse])
def get_upcoming(
    date_from: str,
    user_id: int = Query(..., description="Telegram User ID"),
    limit: int = Query(default=10, ge=1, le=50),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[AppointmentResponse]:
    _parse_date(date_from)
    rows = manager.get_upcoming_appointments(date_from, limit, user_id=user_id)
    return [_to_response(apt) for apt in rows]


@router.get("/{date_str}/conflict/{time_str}", response_model=Optional[AppointmentResponse])
def check_conflict(
    date_str: str,
    time_str: str,
    user_id: int = Query(..., description="Telegram User ID"),
    duration: int = Query(default=_DEFAULT_DURATION_MIN, ge=1, le=480),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> Optional[AppointmentResponse]:
    _parse_date(date_str)
    apts = manager.get_appointments(date_str, user_id=user_id)
    overlap = _find_overlap(apts, time_str, duration)
    if overlap:
        return _to_response(overlap)
    raise HTTPException(status_code=404, detail="Franja libre.")


@router.get("/{date_str}", response_model=List[AppointmentResponse])
def get_appointments(
    date_str: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[AppointmentResponse]:
    _parse_date(date_str)
    return [_to_response(apt) for apt in manager.get_appointments(date_str, user_id=user_id)]


@router.delete("/{date_str}/{index}", status_code=204)
def delete_appointment(
    date_str: str,
    index: int,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> None:
    _parse_date(date_str)
    deleted = manager.delete_appointment(date_str, index, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Cita índice {index} no encontrada el {date_str}.")


@router.put("/{date_str}/{index}", response_model=AppointmentResponse)
def update_appointment(
    date_str: str,
    index: int,
    body: AppointmentUpdate,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> AppointmentResponse:
    _parse_date(date_str)
    try:
        updated = manager.update_appointment(
            date_str, index, time=body.time, name=body.name,
            apt_type=body.type, notes=body.notes, user_id=user_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Cita índice {index} no encontrada el {date_str}.")
    return _to_response(updated)
