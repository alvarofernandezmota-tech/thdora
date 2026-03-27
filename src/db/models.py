"""
Modelos ORM de THDORA.

Tablas:
    appointments  → citas del usuario
    habits        → hábitos diarios del usuario

Diseño:
    - `date` almacenado como string ISO (YYYY-MM-DD) para simplicidad
    - `index` calculado al insertar (número ordinal por día)
    - No hay FK entre tablas — cada día es independiente
"""

from sqlalchemy import Integer, String, Text
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
    """Hábito diario del usuario."""

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
