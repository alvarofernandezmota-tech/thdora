"""
Modelos Pydantic para el endpoint de citas.
"""

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    """Payload de entrada para crear una cita."""
    time: str
    type: str
    notes: str = ""


class AppointmentCreatedResponse(BaseModel):
    """Respuesta tras crear una cita: devuelve el UUID."""
    id: str


class AppointmentResponse(BaseModel):
    """Cita completa devuelta por GET."""
    id: str
    time: str
    type: str
    notes: str
