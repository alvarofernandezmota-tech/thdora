"""
Modelos Pydantic de la API REST de THDORA.

Exporta:
    AppointmentIn  : payload de entrada para crear cita
    AppointmentOut : respuesta con cita creada
    HabitIn        : payload de entrada para registrar hábito
    HabitOut       : respuesta con hábito registrado
"""

from src.api.models.appointment import AppointmentIn, AppointmentOut
from src.api.models.habit import HabitIn, HabitOut

__all__ = ["AppointmentIn", "AppointmentOut", "HabitIn", "HabitOut"]
