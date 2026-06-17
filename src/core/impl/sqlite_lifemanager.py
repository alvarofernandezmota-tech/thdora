"""Implementación SQLite de LifeManager para THDORA — v4 con soporte multi-usuario.

Todos los métodos aceptan user_id: int = 0.
Cuando user_id > 0 filtra por ese usuario.
Cuando user_id == 0 devuelve todos (compatibilidad con datos legacy pre-Sprint5).
"""
from __future__ import annotations

import json
import logging
from datetime import date as date_type, timedelta
from typing import Any

from sqlalchemy.orm import Session

from src.db.models import Appointment, Habit, HabitConfig, UserConfig

logger = logging.getLogger(__name__)


class SQLiteLifeManager:
    """Gestor de datos SQLite. Recibe una SQLAlchemy Session síncrona."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ── Helpers ────────────────────────────────────────────────────────────

    def _filter_user(self, query, model, user_id: int):
        """Aplica filtro user_id si > 0."""
        if user_id > 0:
            query = query.filter(model.user_id == user_id)
        return query

    # ── Appointments ────────────────────────────────────────────────────

    def get_appointments(self, date_str: str, user_id: int = 0) -> list[dict]:
        q = self.session.query(Appointment).filter(Appointment.date == date_str)
        q = self._filter_user(q, Appointment, user_id)
        return [a.to_dict() for a in q.order_by(Appointment.time).all()]

    def get_appointments_range(
        self, date_from: str, date_to: str, user_id: int = 0
    ) -> list[dict]:
        q = self.session.query(Appointment).filter(
            Appointment.date >= date_from,
            Appointment.date <= date_to,
        )
        q = self._filter_user(q, Appointment, user_id)
        return [a.to_dict() for a in q.order_by(Appointment.date, Appointment.time).all()]

    def get_upcoming_appointments(
        self, date_from: str, limit: int = 10, user_id: int = 0
    ) -> list[dict]:
        q = self.session.query(Appointment).filter(Appointment.date >= date_from)
        q = self._filter_user(q, Appointment, user_id)
        return [
            a.to_dict()
            for a in q.order_by(Appointment.date, Appointment.time).limit(limit).all()
        ]

    def create_appointment(
        self,
        date_str: str,
        time: str,
        apt_type: str,
        notes: str = "",
        name: str = "",
        user_id: int = 0,
    ) -> dict:
        # Calcular índice del día para este usuario
        existing = self.get_appointments(date_str, user_id=user_id)
        index = len(existing) + 1
        apt = Appointment(
            date=date_str, time=time, type=apt_type,
            notes=notes, name=name, index=index, user_id=user_id,
        )
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt.to_dict()

    def update_appointment(
        self,
        date_str: str,
        index: int,
        time: str | None = None,
        name: str | None = None,
        apt_type: str | None = None,
        notes: str | None = None,
        user_id: int = 0,
    ) -> dict | None:
        q = self.session.query(Appointment).filter(
            Appointment.date == date_str, Appointment.index == index
        )
        q = self._filter_user(q, Appointment, user_id)
        apt = q.first()
        if not apt:
            return None
        if time is not None:
            apt.time = time
        if name is not None:
            apt.name = name
        if apt_type is not None:
            apt.type = apt_type
        if notes is not None:
            apt.notes = notes
        self.session.commit()
        self.session.refresh(apt)
        return apt.to_dict()

    def delete_appointment(
        self, date_str: str, index: int, user_id: int = 0
    ) -> bool:
        q = self.session.query(Appointment).filter(
            Appointment.date == date_str, Appointment.index == index
        )
        q = self._filter_user(q, Appointment, user_id)
        apt = q.first()
        if not apt:
            return False
        self.session.delete(apt)
        self.session.commit()
        return True

    # ── Habits ────────────────────────────────────────────────────────────────

    def get_habits(self, date_str: str, user_id: int = 0) -> dict[str, str]:
        q = self.session.query(Habit).filter(Habit.date == date_str)
        q = self._filter_user(q, Habit, user_id)
        return {h.habit: h.value for h in q.all()}

    def get_habits_range(
        self, date_from: str, date_to: str, user_id: int = 0
    ) -> dict[str, dict[str, str]]:
        q = self.session.query(Habit).filter(
            Habit.date >= date_from, Habit.date <= date_to
        )
        q = self._filter_user(q, Habit, user_id)
        result: dict[str, dict[str, str]] = {}
        for h in q.all():
            result.setdefault(h.date, {})[h.habit] = h.value
        return result

    def log_habit(
        self, date_str: str, habit: str, value: str, user_id: int = 0
    ) -> dict:
        # Upsert
        q = self.session.query(Habit).filter(
            Habit.date == date_str, Habit.habit == habit
        )
        q = self._filter_user(q, Habit, user_id)
        existing = q.first()
        if existing:
            existing.value = value
            self.session.commit()
            self.session.refresh(existing)
            return existing.to_dict()
        new_habit = Habit(date=date_str, habit=habit, value=value, user_id=user_id)
        self.session.add(new_habit)
        self.session.commit()
        self.session.refresh(new_habit)
        return new_habit.to_dict()

    def update_habit(
        self, date_str: str, habit: str, value: str, user_id: int = 0
    ) -> dict | None:
        q = self.session.query(Habit).filter(
            Habit.date == date_str, Habit.habit == habit
        )
        q = self._filter_user(q, Habit, user_id)
        h = q.first()
        if not h:
            return None
        h.value = value
        self.session.commit()
        self.session.refresh(h)
        return h.to_dict()

    def delete_habit(
        self, date_str: str, habit: str, user_id: int = 0
    ) -> bool:
        q = self.session.query(Habit).filter(
            Habit.date == date_str, Habit.habit == habit
        )
        q = self._filter_user(q, Habit, user_id)
        h = q.first()
        if not h:
            return False
        self.session.delete(h)
        self.session.commit()
        return True

    # ── HabitConfig ─────────────────────────────────────────────────────────

    def get_all_habit_configs(self, user_id: int = 0) -> list[dict]:
        q = self.session.query(HabitConfig)
        q = self._filter_user(q, HabitConfig, user_id)
        return [c.to_dict() for c in q.all()]

    def get_habit_config(self, name: str, user_id: int = 0) -> dict | None:
        q = self.session.query(HabitConfig).filter(HabitConfig.name == name)
        q = self._filter_user(q, HabitConfig, user_id)
        c = q.first()
        return c.to_dict() if c else None

    def upsert_habit_config(
        self,
        name: str,
        habit_type: str = "text",
        unit: str | None = None,
        min_val: float | None = None,
        max_val: float | None = None,
        quick_vals: list[str] | None = None,
        xp_rule: str | None = None,
        user_id: int = 0,
    ) -> dict:
        q = self.session.query(HabitConfig).filter(HabitConfig.name == name)
        q = self._filter_user(q, HabitConfig, user_id)
        cfg = q.first()
        if cfg:
            cfg.habit_type = habit_type
            cfg.unit = unit
            cfg.min_val = min_val
            cfg.max_val = max_val
            cfg.quick_vals = json.dumps(quick_vals or [])
            cfg.xp_rule = xp_rule
        else:
            cfg = HabitConfig(
                name=name, habit_type=habit_type, unit=unit,
                min_val=min_val, max_val=max_val,
                quick_vals=json.dumps(quick_vals or []),
                xp_rule=xp_rule, user_id=user_id,
            )
            self.session.add(cfg)
        self.session.commit()
        self.session.refresh(cfg)
        return cfg.to_dict()

    def delete_habit_config(self, name: str, user_id: int = 0) -> bool:
        q = self.session.query(HabitConfig).filter(HabitConfig.name == name)
        q = self._filter_user(q, HabitConfig, user_id)
        cfg = q.first()
        if not cfg:
            return False
        self.session.delete(cfg)
        self.session.commit()
        return True

    # ── UserConfig ──────────────────────────────────────────────────────────

    def get_user_config(self, user_id: int = 0) -> dict:
        cfg = self.session.query(UserConfig).filter(
            UserConfig.user_id == user_id
        ).first()
        if not cfg:
            # Devolver defaults si no existe
            return {
                "user_id": user_id,
                "daily_summary_enabled": False,
                "daily_summary_time": "08:00",
                "notif_enabled": True,
                "notif_offsets": ["30"],
                "notif_ask_confirm": False,
                "evening_log_enabled": False,
                "evening_log_time": "21:00",
                "timezone": "Europe/Madrid",
            }
        return cfg.to_dict()

    def upsert_user_config(
        self,
        user_id: int = 0,
        daily_summary_enabled: bool | None = None,
        daily_summary_time: str | None = None,
        notif_enabled: bool | None = None,
        notif_offsets: list[str] | None = None,
        notif_ask_confirm: bool | None = None,
        evening_log_enabled: bool | None = None,
        evening_log_time: str | None = None,
        timezone: str | None = None,
    ) -> dict:
        cfg = self.session.query(UserConfig).filter(
            UserConfig.user_id == user_id
        ).first()
        if not cfg:
            cfg = UserConfig(user_id=user_id)
            self.session.add(cfg)
        if daily_summary_enabled is not None:
            cfg.daily_summary_enabled = daily_summary_enabled
        if daily_summary_time is not None:
            cfg.daily_summary_time = daily_summary_time
        if notif_enabled is not None:
            cfg.notif_enabled = notif_enabled
        if notif_offsets is not None:
            cfg.notif_offsets = json.dumps(notif_offsets)
        if notif_ask_confirm is not None:
            cfg.notif_ask_confirm = notif_ask_confirm
        if evening_log_enabled is not None:
            cfg.evening_log_enabled = evening_log_enabled
        if evening_log_time is not None:
            cfg.evening_log_time = evening_log_time
        if timezone is not None:
            cfg.timezone = timezone
        self.session.commit()
        self.session.refresh(cfg)
        return cfg.to_dict()

    # ── Summary ──────────────────────────────────────────────────────────────

    def get_summary(self, date_str: str, user_id: int = 0) -> dict[str, Any]:
        return {
            "date": date_str,
            "appointments": self.get_appointments(date_str, user_id=user_id),
            "habits": self.get_habits(date_str, user_id=user_id),
            "user_config": self.get_user_config(user_id=user_id),
        }
