"""
Cliente HTTP asíncrono para la API REST de THDORA.

Centraliza todas las llamadas HTTP del bot Telegram hacia la FastAPI.
Si la URL de la API cambia, solo hay que tocar este módulo.

Configuración::

    THDORA_API_URL=http://localhost:8000   # por defecto

Uso::

    from src.bot.api_client import ThdoraApiClient

    api = ThdoraApiClient()
    citas = await api.get_appointments("2026-03-24")
"""

import logging
import os
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)

_API_BASE = os.getenv("THDORA_API_URL", "http://localhost:8000")
_TIMEOUT = httpx.Timeout(10.0)


class ApiError(Exception):
    """Error de comunicación con la API de THDORA."""

    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


class ThdoraApiClient:
    """
    Cliente HTTP asíncrono para la API REST de THDORA.

    Cada método lanza ``ApiError`` si la petición falla,
    de modo que los handlers pueden capturar un solo tipo de excepción.

    Attributes:
        base_url (str): URL base de la API (sin trailing slash).

    Example::

        api = ThdoraApiClient()
        await api.health()                                    # True / False
        await api.get_appointments("2026-03-24")              # List[Dict]
        await api.create_appointment("2026-03-24", "10:00", "médica", "notas")
        await api.delete_appointment("uuid-str")
        await api.get_habits("2026-03-24")                    # Dict[str, str]
        await api.log_habit("2026-03-24", "sueno", "8h")
        await api.get_summary("2026-03-24")                   # Dict
    """

    def __init__(self, base_url: str = _API_BASE) -> None:
        self.base_url = base_url.rstrip("/")

    # ── Health ─────────────────────────────────────────────────────────────────

    async def health(self) -> bool:
        """Comprueba si la API está respondiendo. No lanza excepciones."""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                r = await client.get(f"{self.base_url}/")
                return r.status_code == 200
        except httpx.RequestError as exc:
            logger.warning("API no disponible: %s", exc)
            return False

    # ── Appointments ───────────────────────────────────────────────────────────

    async def get_appointments(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Devuelve las citas de un día.

        Args:
            date_str: Fecha en formato ``YYYY-MM-DD``.

        Returns:
            Lista de dicts con claves ``id``, ``time``, ``type``, ``notes``.

        Raises:
            ApiError: Si la petición falla.
        """
        return await self._get(f"/appointments/{date_str}")

    async def create_appointment(
        self,
        date_str: str,
        time: str,
        apt_type: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Crea una nueva cita.

        Args:
            date_str: Fecha en formato ``YYYY-MM-DD``.
            time: Hora en formato ``HH:MM``.
            apt_type: Tipo de cita (``médica``, ``personal``, ``trabajo``, ``otra``).
            notes: Notas opcionales.

        Returns:
            Dict con la cita creada, incluyendo su ``id``.

        Raises:
            ApiError: Si la petición falla o la validación no pasa.
        """
        return await self._post(
            "/appointments",
            json={"date": date_str, "time": time, "type": apt_type, "notes": notes},
        )

    async def delete_appointment(self, apt_id: str) -> bool:
        """
        Elimina una cita por su UUID.

        Args:
            apt_id: UUID de la cita (completo o prefijo de 8 chars).

        Returns:
            ``True`` si se eliminó, ``False`` si no se encontró.

        Raises:
            ApiError: Si hay un error de red.
        """
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(f"{self.base_url}/appointments/{apt_id}")
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red: {exc}") from exc

    # ── Habits ─────────────────────────────────────────────────────────────────

    async def get_habits(self, date_str: str) -> Dict[str, str]:
        """
        Devuelve los hábitos registrados de un día.

        Args:
            date_str: Fecha en formato ``YYYY-MM-DD``.

        Returns:
            Dict ``{hábito: valor}``.

        Raises:
            ApiError: Si la petición falla.
        """
        return await self._get(f"/habits/{date_str}")

    async def log_habit(self, date_str: str, habit: str, value: str) -> bool:
        """
        Registra o actualiza el valor de un hábito.

        Args:
            date_str: Fecha en formato ``YYYY-MM-DD``.
            habit: Nombre del hábito (ej: ``"sueno"``).
            value: Valor del hábito (ej: ``"8h"``).

        Returns:
            ``True`` si se registró correctamente.

        Raises:
            ApiError: Si la petición falla.
        """
        await self._post("/habits", json={"date": date_str, "habit": habit, "value": value})
        return True

    # ── Summary ────────────────────────────────────────────────────────────────

    async def get_summary(self, date_str: str) -> Dict[str, Any]:
        """
        Devuelve el resumen completo del día: citas + hábitos.

        Args:
            date_str: Fecha en formato ``YYYY-MM-DD``.

        Returns:
            Dict con claves ``date``, ``appointments``, ``habits``.

        Raises:
            ApiError: Si la petición falla.
        """
        return await self._get(f"/summary/{date_str}")

    # ── Internals ──────────────────────────────────────────────────────────────

    async def _get(self, path: str) -> Any:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.get(f"{self.base_url}{path}")
                _raise_for_status(r)
                return r.json()
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red en GET {path}: {exc}") from exc

    async def _post(self, path: str, json: Dict[str, Any]) -> Any:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.post(f"{self.base_url}{path}", json=json)
                _raise_for_status(r)
                return r.json()
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red en POST {path}: {exc}") from exc


def _raise_for_status(r: httpx.Response) -> None:
    """Lanza ApiError si el status HTTP indica fallo."""
    if r.is_error:
        detail = ""
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = r.text[:200]
        raise ApiError(f"HTTP {r.status_code}: {detail}", status_code=r.status_code)
