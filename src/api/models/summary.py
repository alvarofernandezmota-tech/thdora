"""
Modelos Pydantic para el resumen diario.
"""

from typing import Dict, List
from pydantic import BaseModel


class AppointmentSummary(BaseModel):
    id: str
    time: str
    type: str
    notes: str = ""


class DaySummaryResponse(BaseModel):
    date: str
    appointments: List[AppointmentSummary]
    habits: Dict[str, str]
