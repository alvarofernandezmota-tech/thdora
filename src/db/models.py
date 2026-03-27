"""
Modelos ORM de THDORA.

Tablas:
    appointments   → citas del usuario
    habits         → registros diarios de hábitos
    habit_config   → configuración por hábito (tipo, unidad, botones rápidos, regla XP)

Diseño:
    - `date` almacenado como string ISO (YYYY-MM-DD) para simplicidad
    - `index` calculado al insertar (número ordinal por día)
    - No hay FK entre tablas — cada día es independiente
    - `habit_config.quick_vals` almacenado como JSON string (lista separada por comas)
"""

from sqlalchemy import Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Appointment(Base):
    """Cita del usuario."""

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    time: Mapped[str] = mapped_column(String(5), nullable=False)               # HH:MM
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="otra")
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)     # ordinal por día

    def to_dict(self) -> dict:
        return {
            "id": self.id,
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
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    habit: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
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
        Regla para calcular XP en F10 RPG.
        Formato: "gte:7" (mayor o igual a 7), "any" (cualquier valor), "eq:0" (igual a 0)
        None si el hábito no otorga XP.
    """

    __tablename__ = "habit_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)  # nombre del hábito
    habit_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text")  # numeric|time|boolean|text
    unit: Mapped[str] = mapped_column(String(20), nullable=True)                 # "h", "min", "L", ""
    min_val: Mapped[float] = mapped_column(Float, nullable=True)                 # valor mínimo (para numeric/time)
    max_val: Mapped[float] = mapped_column(Float, nullable=True)                 # valor máximo
    quick_vals: Mapped[str] = mapped_column(String(200), nullable=True)          # "6h,7h,8h,9h"
    xp_rule: Mapped[str] = mapped_column(String(50), nullable=True)              # "gte:7", "any", "eq:0"

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
