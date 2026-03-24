"""
Modelos Pydantic para el dominio de citas (appointments).

Usados para validación de entrada y serialización de salida en la API REST.
"""

from pydantic import BaseModel, field_validator
from src.core.impl.memory_lifemanager import VALID_TYPES, _TIME_RE


class AppointmentCreate(BaseModel):
    """Payload para crear una cita.

    Attributes:
        time (str): Hora en formato HH:MM.
        type (str): Tipo de cita. Debe ser uno de los valores permitidos.
        notes (str): Notas opcionales.
    """

    time: str
    type: str
    notes: str = ""

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not _TIME_RE.match(v):
            raise ValueError(
                f"Formato de hora inválido: '{v}'. Se espera HH:MM (ej: '09:30')."
            )
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(
                f"Tipo de cita inválido: '{v}'. "
                f"Valores permitidos: {sorted(VALID_TYPES)}"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "time": "10:30",
                "type": "médica",
                "notes": "llevar analítica",
            }
        }
    }


class AppointmentResponse(BaseModel):
    """Representación de una cita en la respuesta de la API.

    Attributes:
        id (str): UUID de la cita.
        time (str): Hora en formato HH:MM.
        type (str): Tipo de la cita.
        notes (str): Notas de la cita.
    """

    id: str
    time: str
    type: str
    notes: str


class AppointmentCreatedResponse(BaseModel):
    """Respuesta tras crear una cita satisfactoriamente.

    Attributes:
        id (str): UUID asignado a la nueva cita.
    """

    id: str
