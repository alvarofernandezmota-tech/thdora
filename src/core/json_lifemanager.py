"""
Implementación con persistencia JSON de AbstractLifeManager.

Propósito:
    Implementación para uso personal real. Los datos se guardan en
    ``datos/thdora.json`` y sobreviven al reinicio del proceso.

Cuándo usar:
    - Uso personal en local (un único usuario)
    - Cuando la persistencia entre sesiones es necesaria
    - Bot Telegram y API en producción local

Cuándo NO usar:
    - Múltiples usuarios concurrentes (sin locking thread-safe)
    - Cuando se necesitan queries complejas por rango de fechas
    - Producción multiusuario (migrar a SqlLifeManager en Fase 11)

Dependencias:
    Solo stdlib Python: ``json``, ``pathlib``.

Siguiente implementación: SqlLifeManager (Fase 11)
"""

import json
from uuid import uuid4, UUID
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

from src.core.interfaces.abstract_lifemanager import AbstractLifeManager
from src.core.impl.memory_lifemanager import VALID_TYPES, _TIME_RE

_DEFAULT_PATH = Path("datos/thdora.json")


class JsonLifeManager(AbstractLifeManager):
    """
    Gestor de vida personal con persistencia en fichero JSON local.

    Carga los datos al instanciar y los guarda tras cada modificación.
    El fichero se crea automáticamente si no existe.

    Attributes:
        _filepath (Path): Ruta al fichero JSON de datos.
        _data (Dict): Datos cargados en memoria (caché activo).

    Example::

        from src.core.impl.json_lifemanager import JsonLifeManager
        from datetime import date

        mgr = JsonLifeManager()
        mgr.create_appointment(date.today(), "10:00", "médica")
        mgr.log_habit(date.today(), "sueno", "8h")
        # Los datos persisten en datos/thdora.json
    """

    def __init__(self, filepath: Path = _DEFAULT_PATH) -> None:
        """
        Inicializa el gestor y carga los datos existentes del fichero.

        Si el fichero no existe, empieza con datos vacíos.

        Args:
            filepath (Path): Ruta al fichero JSON. Por defecto ``datos/thdora.json``.

        Complejidad: O(n) donde n es el tamaño del fichero.
        """
        self._filepath = filepath
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """
        Carga los datos desde el fichero JSON.

        Returns:
            Dict: Datos cargados, o estructura vacía si el fichero no existe.
        """
        if self._filepath.exists():
            with open(self._filepath, encoding="utf-8") as f:
                return json.load(f)
        return {"appointments": {}, "habits": {}}

    def _save(self) -> None:
        """
        Persiste el estado actual en el fichero JSON.

        Crea el directorio padre si no existe.
        """
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def create_appointment(self, date: date, time: str, type: str, notes: str = "") -> UUID:
        """
        Crea una nueva cita y la persiste en el fichero JSON.

        Args:
            date (date): Fecha de la cita.
            time (str): Hora en formato HH:MM (24h). Ej: ``"10:30"``.
            type (str): Tipo de la cita. Debe ser uno de:
                        ``"médica"``, ``"personal"``, ``"trabajo"``, ``"otra"``.
            notes (str): Notas opcionales.

        Returns:
            UUID: Identificador único asignado a la cita.

        Raises:
            ValueError: Si ``time`` no cumple el formato HH:MM (00:00–23:59).
            ValueError: Si ``type`` no está en los valores permitidos.

        Complejidad: O(n) por la escritura al disco.
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

        if date_str not in self._data["appointments"]:
            self._data["appointments"][date_str] = []

        self._data["appointments"][date_str].append({
            "id": str(apt_id),
            "time": time,
            "type": type,
            "notes": notes,
        })

        self._save()
        return apt_id

    def get_appointments(self, date: date) -> List[Dict]:
        """
        Devuelve las citas de un día.

        Args:
            date (date): Día a consultar.

        Returns:
            List[Dict]: Lista de citas. Lista vacía si no hay ninguna.

        Complejidad: O(1).
        """
        return self._data["appointments"].get(str(date), [])

    def delete_appointment(self, date: date, index: int) -> bool:
        """
        Elimina una cita por su posición en la lista del día y persiste.

        Args:
            date (date): Día de la cita a eliminar.
            index (int): Posición 0-based de la cita en la lista del día.

        Returns:
            bool: ``True`` si la cita fue eliminada correctamente.

        Raises:
            IndexError: Si ``index`` está fuera de rango o el día no tiene citas.

        Complejidad: O(n) por pop de lista y escritura al disco.
        """
        date_str = str(date)
        appointments = self._data["appointments"].get(date_str, [])

        if index < 0 or index >= len(appointments):
            raise IndexError(
                f"Índice {index} fuera de rango para {date_str} "
                f"(hay {len(appointments)} cita(s))"
            )

        self._data["appointments"][date_str].pop(index)
        self._save()
        return True

    def log_habit(self, date: date, habit: str, value: str) -> bool:
        """
        Registra o actualiza el valor de un hábito y persiste.

        Args:
            date (date): Día del registro.
            habit (str): Nombre del hábito.
            value (str): Valor del hábito.

        Returns:
            bool: Siempre ``True``.

        Complejidad: O(n) por escritura al disco.
        """
        date_str = str(date)

        if date_str not in self._data["habits"]:
            self._data["habits"][date_str] = {}

        self._data["habits"][date_str][habit] = value
        self._save()
        return True

    def get_habits(self, date: date) -> Dict[str, str]:
        """
        Devuelve los hábitos registrados de un día.

        Args:
            date (date): Día a consultar.

        Returns:
            Dict[str, str]: Diccionario {hábito: valor}.
                            Diccionario vacío si no hay registros.

        Complejidad: O(1).
        """
        return self._data["habits"].get(str(date), {})

    def get_day_summary(self, date: date) -> Dict:
        """
        Devuelve el resumen completo del día: citas + hábitos.

        Args:
            date (date): Día a consultar.

        Returns:
            Dict: Resumen estructurado con claves ``date``,
                  ``appointments`` y ``habits``.

        Complejidad: O(1).
        """
        return {
            "date": str(date),
            "appointments": self.get_appointments(date),
            "habits": self.get_habits(date),
        }
