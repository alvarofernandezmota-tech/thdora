"""
Modelos ORM de THDORA.

Tablas:
    appointments   → citas del usuario
    habits         → registros diarios de hábitos
    habit_config   → configuración por hábito (tipo, unidad, botones rápidos, regla XP)
    user_config    → configuración de notificaciones del usuario (F12)

Diseño:
    - `date` almacenado como string ISO (YYYY-MM-DD) para simplicidad
    - `index` calculado al insertar (número ordinal por día)
    - `telegram_user_id` en appointments y habits garantiza aislamiento multi-usuario
    - No hay FK entre tablas — cada día es independiente
    - `habit_config.quick_vals` almacenado como JSON string (lista separada por comas)
    - `user_config.notif_offsets` almacenado como string CSV ("60,30,15")
    - `user_config` usa upsert por `user_id` — preparado para multi-usuario (F11)
"""

from sqlalchemy import Boolean, Integer, String, Text, Float, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Appointment(Base):
    """Cita del usuario."""

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    time: Mapped[str] = mapped_column(String(5), nullable=False)               # HH:MM
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="otra")
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)     # ordinal por día

    __table_args__ = (
        Index("ix_appointments_user_date", "telegram_user_id", "date"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "telegram_user_id": self.telegram_user_id,
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
    telegram_user_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    habit: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        Index("ix_habits_user_date", "telegram_user_id", "date"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "telegram_user_id": self.telegram_user_id,
            "date": self.date,
            "habit": self.habit,
            "value": self.value,
        }


class HabitConfig(Base):
    """
    Configuración de cada hábito.

    Tipos soportados:
        numeric  → valor numérico (humor 1-10, vasos de agua)
        time     → duración (sueño en horas, ejercicio en minutos)
        boolean  → sí / no (THC, tabaco)
        text     → texto libre (alimentación, notas)

    quick_vals:
        Lista separada por comas: "6h,7h,8h,9h" → botones rápidos en el bot
        None si no hay botones rápidos.

    xp_rule:
        Regla para calcular XP en F15 Gamificación.
        Formato: "gte:7" (mayor o igual a 7), "any" (cualquier valor), "eq:0" (igual a 0)
        None si el hábito no otorga XP.
    """

    __tablename__ = "habit_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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
            "name": self.name,
            "habit_type": self.habit_type,
            "unit": self.unit,
            "min_val": self.min_val,
            "max_val": self.max_val,
            "quick_vals": self.quick_vals.split(",") if self.quick_vals else [],
            "xp_rule": self.xp_rule,
        }


class UserConfig(Base):
    """
    Configuración de notificaciones del usuario (F12).

    Campos v1:
        daily_summary_enabled  → resumen diario activo
        daily_summary_time     → hora del resumen diario (HH:MM)
        notif_enabled          → avisos de cita activos
        notif_offsets          → minutos antes de cada cita (CSV: "60,30,15")
        notif_ask_confirm      → preguntar ¿vas? en el aviso
        evening_log_enabled    → resumen nocturno de hábitos activo
        evening_log_time       → hora del resumen nocturno (HH:MM)
        timezone               → zona horaria del usuario

    Upsert:
        GET /user_config/{user_id} crea la fila con defaults si no existe.
        El usuario nunca ve un error por "no configurado".
    """

    __tablename__ = "user_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

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
