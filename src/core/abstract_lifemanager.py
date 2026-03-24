"""
Interfaz abstracta principal del ecosistema THDORA.

Define el contrato que toda implementación de gestión de vida debe cumplir.
Cualquier clase que implemente esta interfaz puede ser intercambiada sin
modificar el código que la consume (Liskov Substitution Principle).

Implementaciones disponibles:
    - MemoryLifeManager  : datos en memoria (desarrollo/testing)
    - JsonLifeManager    : persistencia JSON local (pendiente - Fase 5)
    - ApiLifeManager     : sincronización con API REST (pendiente - Fase 6)

Ejemplo de uso::

    from src.core.interfaces import AbstractLifeManager
    from src.core.impl import MemoryLifeManager

    mgr: AbstractLifeManager = MemoryLifeManager()
    cita_id = mgr.create_appointment(date.today(), "10:00", "médica")
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import date
from uuid import UUID


class AbstractLifeManager(ABC):
    """
    Contrato abstracto para el gestor de vida personal de THDORA.

    Agrupa dos dominios:
        1. **Citas** (appointments): eventos con fecha, hora y tipo.
        2. **Hábitos** (habits): valores diários de seguimiento personal
           (sueño, THC, tabaco, ejercicio, etc.)

    Toda implementación concreta DEBE implementar todos los métodos
    marcados con ``@abstractmethod``.
    """

    @abstractmethod
    def create_appointment(self, date: date, time: str, type: str, notes: str = "") -> UUID:
        """
        Crea una nueva cita en el sistema.

        Args:
            date (date): Fecha de la cita. Formato: ``date(2026, 3, 24)``.
            time (str): Hora de inicio en formato HH:MM (24h). Ej: ``"10:30"``.
            type (str): Tipo o título de la cita. Ej: ``"médica"``, ``"trabajo"``.
            notes (str, optional): Notas adicionales. Por defecto cadena vacía.

        Returns:
            UUID: Identificador único de la cita creada.

        Raises:
            ValueError: Si ``time`` no tiene formato HH:MM válido.
            ValueError: Si ``type`` no es un valor permitido.

        Example::

            cita_id = mgr.create_appointment(
                date(2026, 3, 24), "10:00", "médica", "llevar analítica"
            )
        """
        pass

    @abstractmethod
    def get_appointments(self, date: date) -> List[Dict]:
        """
        Devuelve todas las citas de un día concreto.

        Args:
            date (date): Día a consultar.

        Returns:
            List[Dict]: Lista de diccionarios con estructura::

                [
                    {
                        "id": "uuid-string",
                        "time": "HH:MM",
                        "type": "string",
                        "notes": "string"
                    },
                    ...
                ]

            Lista vacía si no hay citas para ese día.

        Example::

            citas = mgr.get_appointments(date(2026, 3, 24))
            for cita in citas:
                print(f"{cita['time']} — {cita['type']}")
        """
        pass

    @abstractmethod
    def delete_appointment(self, date: date, index: int) -> bool:
        """
        Elimina una cita por su posición en la lista del día.

        Args:
            date (date): Día de la cita a eliminar.
            index (int): Posición 0-based de la cita en la lista del día.

        Returns:
            bool: ``True`` si la cita fue eliminada correctamente.

        Raises:
            IndexError: Si ``index`` está fuera del rango de citas del día
                        o si el día no tiene citas.

        Example::

            mgr.create_appointment(date.today(), "10:00", "médica")
            mgr.delete_appointment(date.today(), 0)
            assert mgr.get_appointments(date.today()) == []
        """
        pass

    @abstractmethod
    def log_habit(self, date: date, habit: str, value: str) -> bool:
        """
        Registra el valor de un hábito para un día concreto.

        Hábitos habituales: ``"sueno"``, ``"THC"``, ``"tabaco"``,
        ``"ejercicio"``, ``"agua"``, ``"humor"``.

        Args:
            date (date): Día al que pertenece el registro.
            habit (str): Nombre del hábito. Ej: ``"sueno"``.
            value (str): Valor del hábito. Ej: ``"8h"``, ``"0"``, ``"3km"``.

        Returns:
            bool: ``True`` si el registro fue exitoso.

        Example::

            mgr.log_habit(date.today(), "sueno", "7h30m")
            mgr.log_habit(date.today(), "THC", "0")
        """
        pass

    @abstractmethod
    def get_habits(self, date: date) -> Dict[str, str]:
        """
        Devuelve todos los hábitos registrados para un día concreto.

        Args:
            date (date): Día a consultar.

        Returns:
            Dict[str, str]: Diccionario ``{habit: value}``::

                {
                    "sueno": "8h",
                    "THC": "0",
                    "ejercicio": "30min"
                }

            Diccionario vacío si no hay registros para ese día.
        """
        pass

    @abstractmethod
    def get_day_summary(self, date: date) -> Dict:
        """
        Devuelve el resumen completo de un día: citas + hábitos.

        Args:
            date (date): Día a consultar.

        Returns:
            Dict: Estructura completa del día::

                {
                    "date": "YYYY-MM-DD",
                    "appointments": [ ... ],  # ver get_appointments()
                    "habits": { ... }          # ver get_habits()
                }

        Example::

            summary = mgr.get_day_summary(date.today())
            print(f"Citas: {len(summary['appointments'])}")
            print(f"Hábitos: {summary['habits']}")
        """
        pass
