"""
Implementación en memoria de AbstractLifeManager.

Propósito:
    Implementación más simple posible para desarrollo y testing.
    Los datos se almacenan en diccionarios Python en RAM.
    Se pierden al reiniciar el proceso.

Cuándo usar:
    - Tests unitarios (sin efectos secundarios en disco)
    - Desarrollo local para probar lógica de negocio
    - Demostraciones rápidas

Cuándo NO usar:
    - Producción (datos no persisten)
    - Más de una sesión de trabajo

Próxima implementación: JsonLifeManager (Fase 5)
"""

import re
from uuid import uuid4, UUID
from datetime import date
from typing import List, Dict, FrozenSet

from src.core.interfaces.abstract_lifemanager import AbstractLifeManager

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
VALID_TYPES: FrozenSet[str] = frozenset({"médica", "personal", "trabajo", "otra"})


class MemoryLifeManager(AbstractLifeManager):
    """
    Gestor de vida personal con almacenamiento en memoria.

    Almacena citas y hábitos en diccionarios Python indexados por fecha
    (string ``"YYYY-MM-DD"``) para búsqueda O(1) por día.

    Attributes:
        appointments (Dict[str, List[Dict]]): Citas indexadas por fecha.
        habits (Dict[str, Dict[str, str]]): Hábitos indexados por fecha.
    """

    def __init__(self) -> None:
        self.appointments: Dict[str, List[Dict]] = {}
        self.habits: Dict[str, Dict[str, str]] = {}

    def create_appointment(self, date: date, time: str, type: str, notes: str = "") -> UUID:
        """
        Crea una nueva cita y la almacena en memoria.

        Args:
            date (date): Fecha de la cita.
            time (str): Hora en formato HH:MM (24h).
            type (str): Tipo de cita: ``"médica"``, ``"personal"``, ``"trabajo"``, ``"otra"``.
            notes (str): Notas opcionales.

        Returns:
            UUID: Identificador único asignado a la cita.

        Raises:
            ValueError: Si ``time`` no tiene formato HH:MM válido.
            ValueError: Si ``type`` no es un valor permitido.
        """
        if not _TIME_RE.match(time):
            raise ValueError(
                f"Formato de hora inválido: '{time}'. Se espera HH:MM (ej: '09:30', '23:00')."
            )
        if type not in VALID_TYPES:
            raise ValueError(
                f"Tipo de cita inválido: '{type}'. "
                f"Valores permitidos: {sorted(VALID_TYPES)}"
            )

        apt_id = uuid4()
        date_str = str(date)

        if date_str not in self.appointments:
            self.appointments[date_str] = []

        self.appointments[date_str].append({
            "id": str(apt_id),
            "time": time,
            "type": type,
            "notes": notes,
        })

        return apt_id

    def get_appointments(self, date: date) -> List[Dict]:
        return self.appointments.get(str(date), [])

    def delete_appointment(self, date: date, index: int) -> bool:
        """
        Elimina una cita por su posición en la lista del día.

        Raises:
            IndexError: Si ``index`` está fuera de rango o el día no tiene citas.
        """
        date_str = str(date)
        citas = self.appointments.get(date_str, [])

        if not citas or index < 0 or index >= len(citas):
            raise IndexError(
                f"Índice {index} fuera de rango para {date_str} "
                f"(hay {len(citas)} cita(s))"
            )

        self.appointments[date_str].pop(index)
        return True

    def log_habit(self, date: date, habit: str, value: str) -> bool:
        date_str = str(date)
        if date_str not in self.habits:
            self.habits[date_str] = {}
        self.habits[date_str][habit] = value
        return True

    def get_habits(self, date: date) -> Dict[str, str]:
        return self.habits.get(str(date), {})

    def get_day_summary(self, date: date) -> Dict:
        return {
            "date": str(date),
            "appointments": self.get_appointments(date),
            "habits": self.get_habits(date),
        }
