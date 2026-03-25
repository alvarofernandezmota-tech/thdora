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

from uuid import uuid4, UUID
from datetime import date
from typing import List, Dict

from src.core.interfaces.abstract_lifemanager import AbstractLifeManager


class MemoryLifeManager(AbstractLifeManager):
    """
    Gestor de vida personal con almacenamiento en memoria.

    Almacena citas y hábitos en diccionarios Python indexados por fecha
    (string ``"YYYY-MM-DD"``) para búsqueda O(1) por día.

    Attributes:
        appointments (Dict[str, List[Dict]]): Citas indexadas por fecha.
        habits (Dict[str, Dict[str, str]]): Hábitos indexados por fecha.

    Example::

        from src.core.impl import MemoryLifeManager
        from datetime import date

        mgr = MemoryLifeManager()
        mgr.create_appointment(date.today(), "10:00", "Médico")
        mgr.log_habit(date.today(), "sueno", "8h")
        print(mgr.get_day_summary(date.today()))
    """

    def __init__(self) -> None:
        """
        Inicializa los almacenes de datos en memoria.

        Complejidad: O(1)
        """
        self.appointments: Dict[str, List[Dict]] = {}
        self.habits: Dict[str, Dict[str, str]] = {}

    def create_appointment(self, date: date, time: str, type: str, notes: str = "") -> UUID:
        """
        Crea una nueva cita y la almacena en memoria.

        Genera un UUID v4 único para identificar la cita.
        Crea la lista del día si no existe.

        Args:
            date (date): Fecha de la cita.
            time (str): Hora en formato HH:MM.
            type (str): Tipo/título de la cita.
            notes (str): Notas opcionales.

        Returns:
            UUID: Identificador único asignado a la cita.

        Complejidad: O(1)
        """
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
        """
        Devuelve las citas de un día.

        Args:
            date (date): Día a consultar.

        Returns:
            List[Dict]: Lista de citas. Lista vacía si no hay ninguna.

        Complejidad: O(1)
        """
        return self.appointments.get(str(date), [])

    def delete_appointment(self, date: date, index: int) -> bool:
        """
        Elimina una cita por su posición en la lista del día.

        Args:
            date (date): Día de la cita a eliminar.
            index (int): Posición 0-based de la cita en la lista del día.

        Returns:
            bool: ``True`` si la cita fue eliminada correctamente.

        Raises:
            IndexError: Si ``index`` está fuera del rango de citas del día,
                        si el día no tiene citas, o si el índice es negativo.

        Complejidad: O(n)
        """
        date_str = str(date)
        citas = self.appointments.get(date_str, [])

        if not citas or index < 0 or index >= len(citas):
            raise IndexError(
                f"Índice {index} fuera de rango para el día {date_str} "
                f"({len(citas)} citas)"
            )

        self.appointments[date_str].pop(index)
        return True

    def log_habit(self, date: date, habit: str, value: str) -> bool:
        """
        Registra o actualiza el valor de un hábito para un día.

        Si el hábito ya existía para ese día, sobreescribe el valor.

        Args:
            date (date): Día del registro.
            habit (str): Nombre del hábito (ej: ``"sueno"``, ``"THC"``)
            value (str): Valor del hábito (ej: ``"8h"``, ``"0"``)

        Returns:
            bool: Siempre ``True`` en esta implementación.

        Complejidad: O(1)
        """
        date_str = str(date)

        if date_str not in self.habits:
            self.habits[date_str] = {}

        self.habits[date_str][habit] = value
        return True

    def get_habits(self, date: date) -> Dict[str, str]:
        """
        Devuelve los hábitos registrados de un día.

        Args:
            date (date): Día a consultar.

        Returns:
            Dict[str, str]: Diccionario {hábito: valor}.
                            Diccionario vacío si no hay registros.

        Complejidad: O(1)
        """
        return self.habits.get(str(date), {})

    def get_day_summary(self, date: date) -> Dict:
        """
        Devuelve el resumen completo del día: citas + hábitos.

        Args:
            date (date): Día a consultar.

        Returns:
            Dict: Resumen estructurado con claves ``date``,
                  ``appointments`` y ``habits``.

        Complejidad: O(1)
        """
        return {
            "date": str(date),
            "appointments": self.get_appointments(date),
            "habits": self.get_habits(date),
        }
