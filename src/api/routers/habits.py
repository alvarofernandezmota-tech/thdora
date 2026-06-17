"""
Router de hábitos — v2.1 (multi-user).
"""

from datetime import date as date_type, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

router = APIRouter(prefix="/habits", tags=["habits"])


class HabitCreate(BaseModel):
    habit: str
    value: str


class HabitUpdate(BaseModel):
    value: str


class HabitResponse(BaseModel):
    habit: str
    value: str


class HabitDayResponse(BaseModel):
    date: str
    habits: Dict[str, str]


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


@router.post("/{date_str}", status_code=201)
def log_habit(
    date_str: str,
    body: HabitCreate,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> HabitResponse:
    _parse_date(date_str)
    result = manager.log_habit(date_str, body.habit, body.value, user_id=user_id)
    return HabitResponse(habit=result["habit"], value=result["value"])


@router.get("/week/{date_str}", response_model=List[HabitDayResponse])
def get_habits_week(
    date_str: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[HabitDayResponse]:
    _parse_date(date_str)
    monday, sunday = _week_bounds(date_str)
    data = manager.get_habits_range(monday, sunday, user_id=user_id)
    return [HabitDayResponse(date=d, habits=h) for d, h in sorted(data.items())]


@router.get("/range/{date_from}/{date_to}", response_model=List[HabitDayResponse])
def get_habits_range(
    date_from: str,
    date_to: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[HabitDayResponse]:
    _parse_date(date_from)
    _parse_date(date_to)
    data = manager.get_habits_range(date_from, date_to, user_id=user_id)
    return [HabitDayResponse(date=d, habits=h) for d, h in sorted(data.items())]


@router.get("/stats/{habit_name}", response_model=List[HabitDayResponse])
def get_habit_stats(
    habit_name: str,
    user_id: int = Query(..., description="Telegram User ID"),
    days: int = Query(default=30, ge=1, le=365),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[HabitDayResponse]:
    from datetime import date as dt
    today = str(dt.today())
    date_from = str(dt.today() - timedelta(days=days))
    data = manager.get_habits_range(date_from, today, user_id=user_id)
    return [
        HabitDayResponse(date=d, habits={habit_name: h[habit_name]})
        for d, h in sorted(data.items())
        if habit_name in h
    ]


@router.get("/{date_str}", response_model=List[HabitResponse])
def get_habits(
    date_str: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> List[HabitResponse]:
    _parse_date(date_str)
    habits = manager.get_habits(date_str, user_id=user_id)
    return [HabitResponse(habit=k, value=v) for k, v in habits.items()]


@router.delete("/{date_str}/{habit}", status_code=204)
def delete_habit(
    date_str: str,
    habit: str,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> None:
    _parse_date(date_str)
    deleted = manager.delete_habit(date_str, habit, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Hábito '{habit}' no encontrado el {date_str}.")


@router.put("/{date_str}/{habit}", response_model=HabitResponse)
def update_habit(
    date_str: str,
    habit: str,
    body: HabitUpdate,
    user_id: int = Query(..., description="Telegram User ID"),
    manager: SQLiteLifeManager = Depends(get_manager),
) -> HabitResponse:
    _parse_date(date_str)
    updated = manager.update_habit(date_str, habit, body.value, user_id=user_id)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Hábito '{habit}' no encontrado el {date_str}.")
    return HabitResponse(habit=updated["habit"], value=updated["value"])
