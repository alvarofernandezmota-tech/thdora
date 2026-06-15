"""
SQLiteLifeManager — implementación persistente de AbstractLifeManager.

v2: aislamiento multi-usuario completo.
    Todos los métodos que tocan appointments y habits aceptan user_id
    (telegram_user_id: int) y filtran por él. Sin user_id válido (> 0)
    se lanza ValueError para evitar accesos cruzados entre usuarios.

Uso::

    manager = SQLiteLifeManager()
    manager.create_appointment("2026-03-27", "10:00", "médica", "Dr. Smith",
                               name="Dentista", user_id=123456789)
    appointments = manager.get_appointments("2026-03-27", user_id=123456789)
"""

from typing import Any

from sqlalchemy import and_

from src.core.interfaces.abstract_lifemanager import AbstractLifeManager
from src.db.base import get_session, init_db
from src.db.models import Appointment, Habit, HabitConfig, UserConfig


def _require_user_id(user_id: int) -> None:
    """Lanza ValueError si user_id no es válido (0 o negativo)."""
    if not user_id or user_id <= 0:
        raise ValueError(
            "telegram_user_id es obligatorio y debe ser > 0. "
            "Comprueba que el handler extrae update.effective_user.id correctamente."
        )


class SQLiteLifeManager(AbstractLifeManager):
    """Implementación de AbstractLifeManager con persistencia SQLite + aislamiento por usuario."""

    def __init__(self) -> None:
        init_db()

    # ── Citas ────────────────────────────────────────────────────────────

    def get_appointments(self, date: str, user_id: int = 0) -> list[dict]:
        """Devuelve citas del día filtradas por usuario."""
        _require_user_id(user_id)
        with get_session() as session:
            rows = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date == date,
                        Appointment.telegram_user_id == user_id,
                    )
                )
                .order_by(Appointment.time)
                .all()
            )
            return [r.to_dict() for r in rows]

    def create_appointment(
        self,
        date: str,
        time: str,
        apt_type: str,
        notes: str = "",
        name: str = "",
        user_id: int = 0,
    ) -> dict:
        """Crea una cita con índice ordinal por usuario+día."""
        _require_user_id(user_id)
        if not self._valid_time(time):
            raise ValueError(f"Hora inválida: {time}")
        if apt_type not in ("médica", "personal", "trabajo", "otra"):
            raise ValueError(f"Tipo inválido: {apt_type}")

        with get_session() as session:
            count = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date == date,
                        Appointment.telegram_user_id == user_id,
                    )
                )
                .count()
            )
            apt = Appointment(
                telegram_user_id=user_id,
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

    def delete_appointment(self, date: str, index: int, user_id: int = 0) -> bool:
        """Borra una cita por índice, solo si pertenece al usuario."""
        _require_user_id(user_id)
        with get_session() as session:
            apt = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date == date,
                        Appointment.index == index,
                        Appointment.telegram_user_id == user_id,
                    )
                )
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
        user_id: int = 0,
    ) -> dict | None:
        """Edita campos de una cita, solo si pertenece al usuario."""
        _require_user_id(user_id)
        with get_session() as session:
            apt = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date == date,
                        Appointment.index == index,
                        Appointment.telegram_user_id == user_id,
                    )
                )
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

    def get_appointments_range(
        self, date_from: str, date_to: str, user_id: int = 0
    ) -> list[dict]:
        """Citas en rango de fechas para un usuario concreto."""
        _require_user_id(user_id)
        with get_session() as session:
            rows = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date >= date_from,
                        Appointment.date <= date_to,
                        Appointment.telegram_user_id == user_id,
                    )
                )
                .order_by(Appointment.date, Appointment.time)
                .all()
            )
            return [r.to_dict() for r in rows]

    def get_upcoming_appointments(
        self, from_date: str, limit: int = 10, user_id: int = 0
    ) -> list[dict]:
        """Próximas citas desde from_date para un usuario concreto."""
        _require_user_id(user_id)
        with get_session() as session:
            rows = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date >= from_date,
                        Appointment.telegram_user_id == user_id,
                    )
                )
                .order_by(Appointment.date, Appointment.time)
                .limit(limit)
                .all()
            )
            return [r.to_dict() for r in rows]

    def check_appointment_conflict(
        self, date: str, time: str, user_id: int = 0
    ) -> dict | None:
        """Devuelve cita existente a esa hora para el usuario, o None."""
        _require_user_id(user_id)
        with get_session() as session:
            apt = (
                session.query(Appointment)
                .filter(
                    and_(
                        Appointment.date == date,
                        Appointment.time == time,
                        Appointment.telegram_user_id == user_id,
                    )
                )
                .first()
            )
            return apt.to_dict() if apt else None

    # ── Hábitos ──────────────────────────────────────────────────────────

    def get_habits(self, date: str, user_id: int = 0) -> dict[str, str]:
        """Hábitos del día para un usuario concreto."""
        _require_user_id(user_id)
        with get_session() as session:
            rows = (
                session.query(Habit)
                .filter(
                    and_(
                        Habit.date == date,
                        Habit.telegram_user_id == user_id,
                    )
                )
                .order_by(Habit.habit)
                .all()
            )
            return {r.habit: r.value for r in rows}

    def log_habit(
        self, date: str, habit: str, value: str, user_id: int = 0
    ) -> dict:
        """Registra o actualiza un hábito para el usuario (upsert por user+date+habit)."""
        _require_user_id(user_id)
        with get_session() as session:
            existing = (
                session.query(Habit)
                .filter(
                    and_(
                        Habit.date == date,
                        Habit.habit == habit,
                        Habit.telegram_user_id == user_id,
                    )
                )
                .first()
            )
            if existing:
                existing.value = value
                return existing.to_dict()
            h = Habit(
                telegram_user_id=user_id,
                date=date,
                habit=habit,
                value=value,
            )
            session.add(h)
            session.flush()
            return h.to_dict()

    def delete_habit(self, date: str, habit: str, user_id: int = 0) -> bool:
        """Borra un hábito del usuario por nombre."""
        _require_user_id(user_id)
        with get_session() as session:
            h = (
                session.query(Habit)
                .filter(
                    and_(
                        Habit.date == date,
                        Habit.habit == habit,
                        Habit.telegram_user_id == user_id,
                    )
                )
                .first()
            )
            if not h:
                return False
            session.delete(h)
            return True

    def update_habit(
        self, date: str, habit: str, value: str, user_id: int = 0
    ) -> dict | None:
        """Actualiza el valor de un hábito existente del usuario."""
        _require_user_id(user_id)
        with get_session() as session:
            h = (
                session.query(Habit)
                .filter(
                    and_(
                        Habit.date == date,
                        Habit.habit == habit,
                        Habit.telegram_user_id == user_id,
                    )
                )
                .first()
            )
            if not h:
                return None
            h.value = value
            return h.to_dict()

    def get_habits_range(
        self, date_from: str, date_to: str, user_id: int = 0
    ) -> dict[str, dict[str, str]]:
        """Hábitos en rango de fechas para un usuario."""
        _require_user_id(user_id)
        with get_session() as session:
            rows = (
                session.query(Habit)
                .filter(
                    and_(
                        Habit.date >= date_from,
                        Habit.date <= date_to,
                        Habit.telegram_user_id == user_id,
                    )
                )
                .order_by(Habit.date, Habit.habit)
                .all()
            )
            result: dict[str, dict[str, str]] = {}
            for r in rows:
                result.setdefault(r.date, {})[r.habit] = r.value
            return result

    # ── HabitConfig (sin user_id — configuración global del sistema) ──────

    def get_habit_config(self, name: str) -> dict | None:
        with get_session() as session:
            cfg = session.query(HabitConfig).filter(HabitConfig.name == name).first()
            return cfg.to_dict() if cfg else None

    def get_all_habit_configs(self) -> list[dict]:
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
        with get_session() as session:
            cfg = session.query(HabitConfig).filter(HabitConfig.name == name).first()
            if not cfg:
                return False
            session.delete(cfg)
            return True

    # ── UserConfig ───────────────────────────────────────────────────────

    def get_user_config(self, user_id: str) -> dict:
        with get_session() as session:
            cfg = session.query(UserConfig).filter(UserConfig.user_id == user_id).first()
            if cfg:
                return cfg.to_dict()
            cfg = UserConfig(user_id=user_id)
            session.add(cfg)
            session.flush()
            return cfg.to_dict()

    def upsert_user_config(
        self,
        user_id: str,
        daily_summary_enabled: bool | None = None,
        daily_summary_time: str | None = None,
        notif_enabled: bool | None = None,
        notif_offsets: list[str] | None = None,
        notif_ask_confirm: bool | None = None,
        evening_log_enabled: bool | None = None,
        evening_log_time: str | None = None,
        timezone: str | None = None,
    ) -> dict:
        with get_session() as session:
            cfg = session.query(UserConfig).filter(UserConfig.user_id == user_id).first()
            if not cfg:
                cfg = UserConfig(user_id=user_id)
                session.add(cfg)
                session.flush()
            if daily_summary_enabled is not None:
                cfg.daily_summary_enabled = daily_summary_enabled
            if daily_summary_time is not None:
                cfg.daily_summary_time = daily_summary_time
            if notif_enabled is not None:
                cfg.notif_enabled = notif_enabled
            if notif_offsets is not None:
                cfg.notif_offsets = ",".join(notif_offsets)
            if notif_ask_confirm is not None:
                cfg.notif_ask_confirm = notif_ask_confirm
            if evening_log_enabled is not None:
                cfg.evening_log_enabled = evening_log_enabled
            if evening_log_time is not None:
                cfg.evening_log_time = evening_log_time
            if timezone is not None:
                cfg.timezone = timezone
            return cfg.to_dict()

    # ── Resumen ──────────────────────────────────────────────────────────

    def get_summary(self, date: str, user_id: int = 0) -> dict[str, Any]:
        """Resumen del día: citas + hábitos del usuario."""
        _require_user_id(user_id)
        return {
            "date": date,
            "appointments": self.get_appointments(date, user_id=user_id),
            "habits": self.get_habits(date, user_id=user_id),
        }

    def get_day_summary(self, date: str, user_id: int = 0) -> dict[str, Any]:
        """Alias de get_summary."""
        return self.get_summary(date, user_id=user_id)

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _valid_time(time: str) -> bool:
        import re
        return bool(re.match(r"^([01]?\d|2[0-3]):[0-5]\d$", time))
