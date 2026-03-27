"""
SQLiteLifeManager — implementación persistente de AbstractLifeManager.

Usa SQLAlchemy + SQLite para almacenar citas, hábitos y configuración
de hábitos de forma persistente entre reinicios.

Diferencias respecto a MemoryLifeManager / JsonLifeManager:
    - Los datos persisten en ``data/thdora.db``
    - Los índices son ordinales por día (como en Json)
    - Thread-safe gracias al context manager de sesión
    - Soporta búsqueda por rango de fechas (para /agenda y /upcoming)
    - Soporta HabitConfig (tipos adaptativos F9.2)

Uso::

    manager = SQLiteLifeManager()
    manager.create_appointment("2026-03-27", "10:00", "médica", "Dr. Smith")
    appointments = manager.get_appointments("2026-03-27")
"""

from typing import Any

from sqlalchemy import and_

from src.core.interfaces.abstract_lifemanager import AbstractLifeManager
from src.db.base import get_session, init_db
from src.db.models import Appointment, Habit, HabitConfig


class SQLiteLifeManager(AbstractLifeManager):
    """Implementación de AbstractLifeManager con persistencia SQLite."""

    def __init__(self) -> None:
        init_db()  # crea las tablas si no existen

    # ── Citas ──────────────────────────────────────────────────────

    def get_appointments(self, date: str) -> list[dict]:
        """Devuelve todas las citas de un día ordenadas por hora."""
        with get_session() as session:
            rows = (
                session.query(Appointment)
                .filter(Appointment.date == date)
                .order_by(Appointment.time)
                .all()
            )
            return [r.to_dict() for r in rows]

    def create_appointment(
        self, date: str, time: str, apt_type: str, notes: str = "", name: str = ""
    ) -> dict:
        """Crea una cita y le asigna un índice ordinal para el día."""
        if not self._valid_time(time):
            raise ValueError(f"Hora inválida: {time}")
        if apt_type not in ("médica", "personal", "trabajo", "otra"):
            raise ValueError(f"Tipo inválido: {apt_type}")

        with get_session() as session:
            count = session.query(Appointment).filter(Appointment.date == date).count()
            apt = Appointment(
                date=date,
                time=time,
                name=name,
                type=apt_type,
                notes=notes,
                index=count + 1,
            )
            session.add(apt)
            session.flush()
            return apt.to_dict()

    def delete_appointment(self, date: str, index: int) -> bool:
        """Borra una cita por índice ordinal. Devuelve True si se borró."""
        with get_session() as session:
            apt = (
                session.query(Appointment)
                .filter(and_(Appointment.date == date, Appointment.index == index))
                .first()
            )
            if not apt:
                return False
            session.delete(apt)
            return True

    def update_appointment(
        self,
        date: str,
        index: int,
        time: str | None = None,
        name: str | None = None,
        apt_type: str | None = None,
        notes: str | None = None,
    ) -> dict | None:
        """Edita una cita. Solo actualiza los campos no-None."""
        with get_session() as session:
            apt = (
                session.query(Appointment)
                .filter(and_(Appointment.date == date, Appointment.index == index))
                .first()
            )
            if not apt:
                return None
            if time is not None:
                if not self._valid_time(time):
                    raise ValueError(f"Hora inválida: {time}")
                apt.time = time
            if name is not None:
                apt.name = name
            if apt_type is not None:
                apt.type = apt_type
            if notes is not None:
                apt.notes = notes
            return apt.to_dict()

    def get_appointments_range(self, date_from: str, date_to: str) -> list[dict]:
        """Devuelve citas en un rango de fechas. Útil para /agenda."""
        with get_session() as session:
            rows = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date >= date_from,
                        Appointment.date <= date_to,
                    )
                )
                .order_by(Appointment.date, Appointment.time)
                .all()
            )
            return [r.to_dict() for r in rows]

    def get_upcoming_appointments(self, from_date: str, limit: int = 10) -> list[dict]:
        """Devuelve las próximas citas desde una fecha. Útil para /proximas."""
        with get_session() as session:
            rows = (
                session.query(Appointment)
                .filter(Appointment.date >= from_date)
                .order_by(Appointment.date, Appointment.time)
                .limit(limit)
                .all()
            )
            return [r.to_dict() for r in rows]

    def check_appointment_conflict(self, date: str, time: str) -> dict | None:
        """Devuelve la cita existente a esa hora, o None si no hay conflicto."""
        with get_session() as session:
            apt = (
                session.query(Appointment)
                .filter(and_(Appointment.date == date, Appointment.time == time))
                .first()
            )
            return apt.to_dict() if apt else None

    # ── Hábitos ──────────────────────────────────────────────────────

    def get_habits(self, date: str) -> dict[str, str]:
        """Devuelve los hábitos del día como dict {nombre: valor}."""
        with get_session() as session:
            rows = (
                session.query(Habit)
                .filter(Habit.date == date)
                .order_by(Habit.habit)
                .all()
            )
            return {r.habit: r.value for r in rows}

    def log_habit(self, date: str, habit: str, value: str) -> dict:
        """Registra o actualiza un hábito. Upsert por (date, habit)."""
        with get_session() as session:
            existing = (
                session.query(Habit)
                .filter(and_(Habit.date == date, Habit.habit == habit))
                .first()
            )
            if existing:
                existing.value = value
                return existing.to_dict()
            else:
                h = Habit(date=date, habit=habit, value=value)
                session.add(h)
                session.flush()
                return h.to_dict()

    def delete_habit(self, date: str, habit: str) -> bool:
        """Borra un hábito por nombre. Devuelve True si se borró."""
        with get_session() as session:
            h = (
                session.query(Habit)
                .filter(and_(Habit.date == date, Habit.habit == habit))
                .first()
            )
            if not h:
                return False
            session.delete(h)
            return True

    def update_habit(self, date: str, habit: str, value: str) -> dict | None:
        """Actualiza el valor de un hábito existente."""
        with get_session() as session:
            h = (
                session.query(Habit)
                .filter(and_(Habit.date == date, Habit.habit == habit))
                .first()
            )
            if not h:
                return None
            h.value = value
            return h.to_dict()

    def get_habits_range(self, date_from: str, date_to: str) -> dict[str, dict[str, str]]:
        """Devuelve hábitos en rango de fechas. Útil para /resumen semana."""
        with get_session() as session:
            rows = (
                session.query(Habit)
                .filter(
                    and_(
                        Habit.date >= date_from,
                        Habit.date <= date_to,
                    )
                )
                .order_by(Habit.date, Habit.habit)
                .all()
            )
            result: dict[str, dict[str, str]] = {}
            for r in rows:
                result.setdefault(r.date, {})[r.habit] = r.value
            return result

    # ── HabitConfig ───────────────────────────────────────────────────

    def get_habit_config(self, name: str) -> dict | None:
        """Devuelve la config de un hábito por nombre, o None si no existe."""
        with get_session() as session:
            cfg = session.query(HabitConfig).filter(HabitConfig.name == name).first()
            return cfg.to_dict() if cfg else None

    def get_all_habit_configs(self) -> list[dict]:
        """Devuelve la config de todos los hábitos ordenados por nombre."""
        with get_session() as session:
            rows = session.query(HabitConfig).order_by(HabitConfig.name).all()
            return [r.to_dict() for r in rows]

    def upsert_habit_config(
        self,
        name: str,
        habit_type: str = "text",
        unit: str | None = None,
        min_val: float | None = None,
        max_val: float | None = None,
        quick_vals: list[str] | None = None,
        xp_rule: str | None = None,
    ) -> dict:
        """
        Crea o actualiza la configuración de un hábito.
        quick_vals se almacena como string CSV: ["6h","7h"] → "6h,7h"
        """
        if habit_type not in ("numeric", "time", "boolean", "text"):
            raise ValueError(f"Tipo inválido: {habit_type}. Usa: numeric, time, boolean, text")

        quick_str = ",".join(quick_vals) if quick_vals else None

        with get_session() as session:
            cfg = session.query(HabitConfig).filter(HabitConfig.name == name).first()
            if cfg:
                cfg.habit_type = habit_type
                cfg.unit = unit
                cfg.min_val = min_val
                cfg.max_val = max_val
                cfg.quick_vals = quick_str
                cfg.xp_rule = xp_rule
            else:
                cfg = HabitConfig(
                    name=name,
                    habit_type=habit_type,
                    unit=unit,
                    min_val=min_val,
                    max_val=max_val,
                    quick_vals=quick_str,
                    xp_rule=xp_rule,
                )
                session.add(cfg)
            session.flush()
            return cfg.to_dict()

    def delete_habit_config(self, name: str) -> bool:
        """Borra la configuración de un hábito. Devuelve True si se borró."""
        with get_session() as session:
            cfg = session.query(HabitConfig).filter(HabitConfig.name == name).first()
            if not cfg:
                return False
            session.delete(cfg)
            return True

    # ── Resumen ───────────────────────────────────────────────────────

    def get_summary(self, date: str) -> dict[str, Any]:
        """Devuelve resumen del día: citas + hábitos."""
        return {
            "date": date,
            "appointments": self.get_appointments(date),
            "habits": self.get_habits(date),
        }

    def get_day_summary(self, date: str) -> dict[str, Any]:
        """Alias de get_summary para cumplir con AbstractLifeManager."""
        return self.get_summary(date)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _valid_time(time: str) -> bool:
        import re
        return bool(re.match(r"^([01]?\d|2[0-3]):[0-5]\d$", time))
