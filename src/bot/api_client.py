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

    Rutas reales de la API:
        GET    /appointments/{date}         → listar citas
        POST   /appointments/{date}         → crear cita
        DELETE /appointments/{date}/{index} → eliminar cita por índice
        GET    /habits/{date}               → listar hábitos (List)
        POST   /habits/{date}               → registrar hábito
        GET    /summary/{date}              → resumen del día
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
        """Devuelve las citas de un día como lista de dicts."""
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
        POST /appointments/{date} con body {time, type, notes}
        """
        return await self._post(
            f"/appointments/{date_str}",
            json={"time": time, "type": apt_type, "notes": notes},
        )

    async def delete_appointment(self, date_str: str, index: int) -> bool:
        """
        Elimina una cita por su índice en el día.
        DELETE /appointments/{date}/{index}
        """
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(
                    f"{self.base_url}/appointments/{date_str}/{index}"
                )
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red: {exc}") from exc

    # ── Habits ─────────────────────────────────────────────────────────────────

    async def get_habits(self, date_str: str) -> Dict[str, str]:
        """
        Devuelve los hábitos de un día como Dict {habit: value}.
        La API devuelve List[{habit, value}], se convierte aquí.
        """
        raw: List[Dict[str, str]] = await self._get(f"/habits/{date_str}")
        return {item["habit"]: item["value"] for item in raw}

    async def log_habit(self, date_str: str, habit: str, value: str) -> bool:
        """
        Registra un hábito.
        POST /habits/{date} con body {habit, value}
        """
        await self._post(
            f"/habits/{date_str}",
            json={"habit": habit, "value": value},
        )
        return True

    # ── Summary ────────────────────────────────────────────────────────────────

    async def get_summary(self, date_str: str) -> Dict[str, Any]:
        """Devuelve el resumen completo del día: citas + hábitos."""
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
