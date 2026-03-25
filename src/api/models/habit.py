"""
Modelos Pydantic para el endpoint de hábitos.
"""

from pydantic import BaseModel


class HabitCreate(BaseModel):
    """Payload de entrada para registrar un hábito."""
    habit: str
    value: str


class HabitResponse(BaseModel):
    """Hábito devuelto por GET."""
    habit: str
    value: str
