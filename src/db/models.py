"""
Modelos ORM de THDORA — Sprint 5.
Añadido user_id (Telegram ID) a todas las tablas para multi-usuario.
Nueva tabla AllowedUser para control de acceso desde DB.
"""

from datetime import datetime
from sqlalchemy import Boolean, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Appointment(Base):
    """Cita del usuario."""

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    time: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="otra")
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "time": self.time,
            "name": self.name,
            "type": self.type,
            "notes": self.notes,
            "index": self.index,
        }


class Habit(Base):
    """Registro diario de un hábito."""

    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    habit: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "habit": self.habit,
            "value": self.value,
        }


class HabitConfig(Base):
    """Configuración de cada hábito."""

    __tablename__ = "habit_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    habit_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text")
    unit: Mapped[str] = mapped_column(String(20), nullable=True)
    min_val: Mapped[float] = mapped_column(Float, nullable=True)
    max_val: Mapped[float] = mapped_column(Float, nullable=True)
    quick_vals: Mapped[str] = mapped_column(String(200), nullable=True)
    xp_rule: Mapped[str] = mapped_column(String(50), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "habit_type": self.habit_type,
            "unit": self.unit,
            "min_val": self.min_val,
            "max_val": self.max_val,
            "quick_vals": self.quick_vals.split(",") if self.quick_vals else [],
            "xp_rule": self.xp_rule,
        }


class UserConfig(Base):
    """Configuración de notificaciones del usuario."""

    __tablename__ = "user_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)

    daily_summary_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    daily_summary_time: Mapped[str] = mapped_column(String(5), nullable=False, default="08:00")
    notif_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notif_offsets: Mapped[str] = mapped_column(String(50), nullable=False, default="60,30,15")
    notif_ask_confirm: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    evening_log_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    evening_log_time: Mapped[str] = mapped_column(String(5), nullable=False, default="22:00")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Europe/Madrid")

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "daily_summary_enabled": self.daily_summary_enabled,
            "daily_summary_time": self.daily_summary_time,
            "notif_enabled": self.notif_enabled,
            "notif_offsets": self.notif_offsets.split(",") if self.notif_offsets else ["60", "30", "15"],
            "notif_ask_confirm": self.notif_ask_confirm,
            "evening_log_enabled": self.evening_log_enabled,
            "evening_log_time": self.evening_log_time,
            "timezone": self.timezone,
        }


class AllowedUser(Base):
    """Usuarios permitidos para usar el bot (control admin)."""

    __tablename__ = "allowed_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    added_at: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=lambda: datetime.utcnow().isoformat(),
    )
    added_by: Mapped[int] = mapped_column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "added_at": self.added_at,
            "added_by": self.added_by,
        }
