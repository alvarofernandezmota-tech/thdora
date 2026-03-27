"""
Cliente HTTP asíncrono para la API REST de THDORA.

Centraliza todas las llamadas HTTP del bot Telegram hacia la FastAPI.
Si la URL de la API cambia, solo hay que tocar este módulo.

Configuración::

    THDORA_API_URL=http://localhost:8000   # por defecto

Métodos disponibles::

    # Salud
    await api.health()                                          → bool

    # Citas
    await api.get_appointments("2026-03-27")                    → List[Dict]  (incluye "index")
    await api.create_appointment(date, time, name, type, notes) → Dict
    await api.delete_appointment(date, index)                   → bool
    await api.update_appointment(date, index, ...)              → Dict

    # Hábitos
    await api.get_habits("2026-03-27")                          → Dict[str, str]
    await api.log_habit(date, habit, value)                     → bool
    await api.delete_habit(date, habit)                         → bool
    await api.update_habit(date, habit, value)                  → Dict

    # Resumen
    await api.get_summary("2026-03-27")                         → Dict

Todos los métodos (salvo ``health``) lanzan ``ApiError`` ante cualquier
fallo de red o respuesta HTTP de error.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

_API_BASE = os.getenv("THDORA_API_URL", "http://localhost:8000")
_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)


# ── Excepción pública ────────────────────────────────────────────────────────

class ApiError(Exception):
    """
    Error de comunicación con la API de THDORA.

    Attributes:
        status_code: Código HTTP de la respuesta (0 si fue error de red).
    """

    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


# ── Helper interno ───────────────────────────────────────────────────────

def _raise_for_status(r: httpx.Response) -> None:
    """Lanza ApiError si el status HTTP indica fallo."""
    if r.is_error:
        detail = ""
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = r.text[:200]
        raise ApiError(f"HTTP {r.status_code}: {detail}", status_code=r.status_code)


# ── Cliente ─────────────────────────────────────────────────────────────

class ThdoraApiClient:
    """
    Cliente HTTP asíncrono para la API REST de THDORA.

    Cada método abre y cierra su propio ``AsyncClient`` para evitar
    problemas de event-loop con python-telegram-bot.

    Args:
        base_url: URL base de la API. Por defecto usa ``THDORA_API_URL``.
    """

    def __init__(self, base_url: str = _API_BASE) -> None:
        self.base_url = base_url.rstrip("/")

    # ── Salud ─────────────────────────────────────────────────────────

    async def health(self) -> bool:
        """
        Comprueba si la API responde. No lanza excepciones.

        Returns:
            ``True`` si la API responde con 200, ``False`` en cualquier otro caso.
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                r = await client.get(f"{self.base_url}/")
                return r.status_code == 200
        except httpx.RequestError as exc:
            logger.warning("API no disponible: %s", exc)
            return False

    # ── Citas ─────────────────────────────────────────────────────────

    async def get_appointments(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Devuelve las citas del día con su índice 0-based.

        Returns:
            Lista de dicts con claves: ``index``, ``id``, ``time``,
            ``name``, ``type``, ``notes``.
        """
        return await self._get(f"/appointments/{date_str}")

    async def create_appointment(
        self,
        date_str: str,
        time: str,
        name: str,
        apt_type: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Crea una nueva cita.

        Args:
            date_str: Fecha en formato YYYY-MM-DD.
            time: Hora en formato HH:MM.
            name: Título descriptivo (ej: "Cita con el dentista").
            apt_type: Categoría — ``médica``, ``personal``, ``trabajo``, ``otra``.
            notes: Notas opcionales.
        """
        return await self._post(
            f"/appointments/{date_str}",
            json={"time": time, "name": name, "type": apt_type, "notes": notes},
        )

    async def delete_appointment(self, date_str: str, index: int) -> bool:
        """
        Elimina la cita en la posición ``index`` del día.

        Returns:
            ``True`` si se eliminó, ``False`` si no existía (404).
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
            raise ApiError(f"Error de red DELETE appointment: {exc}") from exc

    async def update_appointment(
        self,
        date_str: str,
        index: int,
        time: Optional[str] = None,
        name: Optional[str] = None,
        apt_type: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Actualiza parcialmente una cita existente.

        Solo se envían los campos que no son ``None``.
        Devuelve la cita completa actualizada.
        """
        payload: Dict[str, Any] = {}
        if time is not None:
            payload["time"] = time
        if name is not None:
            payload["name"] = name
        if apt_type is not None:
            payload["type"] = apt_type
        if notes is not None:
            payload["notes"] = notes
        return await self._put(f"/appointments/{date_str}/{index}", json=payload)

    # ── Hábitos ───────────────────────────────────────────────────────

    async def get_habits(self, date_str: str) -> Dict[str, str]:
        """
        Devuelve los hábitos del día como Dict {habit: value}.

        La API devuelve List[{habit, value}] — se convierte aquí.
        """
        raw: List[Dict[str, str]] = await self._get(f"/habits/{date_str}")
        return {item["habit"]: item["value"] for item in raw}

    async def log_habit(self, date_str: str, habit: str, value: str) -> bool:
        """Registra o sobreescribe un hábito. El valor ya viene calculado."""
        await self._post(
            f"/habits/{date_str}",
            json={"habit": habit, "value": value},
        )
        return True

    async def delete_habit(self, date_str: str, habit: str) -> bool:
        """
        Elimina un hábito concreto del día.

        Returns:
            ``True`` si se eliminó, ``False`` si no existía (404).
        """
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(
                    f"{self.base_url}/habits/{date_str}/{habit}"
                )
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red DELETE habit: {exc}") from exc

    async def update_habit(
        self, date_str: str, habit: str, value: str
    ) -> Dict[str, str]:
        """
        Actualiza el valor de un hábito existente.

        Returns:
            Dict con ``{habit, value}`` actualizado.
        """
        return await self._put(
            f"/habits/{date_str}/{habit}",
            json={"value": value},
        )

    # ── Resumen ───────────────────────────────────────────────────────

    async def get_summary(self, date_str: str) -> Dict[str, Any]:
        """Devuelve el resumen completo del día: citas + hábitos."""
        return await self._get(f"/summary/{date_str}")

    # ── Internals ─────────────────────────────────────────────────────

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

    async def _put(self, path: str, json: Dict[str, Any]) -> Any:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.put(f"{self.base_url}{path}", json=json)
                _raise_for_status(r)
                return r.json()
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red en PUT {path}: {exc}") from exc
