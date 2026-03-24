"""
Modelos Pydantic para el dominio de hábitos (habits).

Usados para validación de entrada y serialización de salida en la API REST.
"""

from pydantic import BaseModel


class HabitCreate(BaseModel):
    """Payload para registrar un hábito.

    Attributes:
        habit (str): Nombre del hábito (ej: ``"sueno"``, ``"THC"``).
        value (str): Valor del hábito (ej: ``"8h"``, ``"0"``).
    """

    habit: str
    value: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "habit": "sueno",
                "value": "8h",
            }
        }
    }


class HabitResponse(BaseModel):
    """Representación de un hábito en la respuesta de la API.

    Attributes:
        habit (str): Nombre del hábito.
        value (str): Valor registrado.
    """

    habit: str
    value: str
