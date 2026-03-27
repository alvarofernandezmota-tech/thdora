"""
Cliente HTTP asíncrono para la API REST de THDORA.

Centraliza todas las llamadas HTTP del bot Telegram hacia la FastAPI.
Si la URL de la API cambia, solo hay que tocar este módulo.

Configuración::

    THDORA_API_URL=http://localhost:8000   # por defecto

Métodos disponibles::

    # Salud
    await api.health()                                             → bool

    # Citas
    await api.get_appointments("2026-03-27")                       → List[Dict]
    await api.create_appointment(date, time, name, type, notes)    → Dict
    await api.delete_appointment(date, index)                      → bool
    await api.update_appointment(date, index, ...)                 → Dict
    await api.check_appointment_conflict(date, time)               → Dict | None

    # Hábitos
    await api.get_habits("2026-03-27")                             → Dict[str, str]
    await api.log_habit(date, habit, value)                        → bool
    await api.delete_habit(date, habit)                            → bool
    await api.update_habit(date, habit, value)                     → Dict

    # HabitConfig (F9.2)
    await api.get_habit_config(name)                               → Dict | None
    await api.get_all_habit_configs()                              → List[Dict]
    await api.upsert_habit_config(name, habit_type, ...)           → Dict
    await api.delete_habit_config(name)                            → bool

    # Resumen
    await api.get_summary("2026-03-27")                            → Dict

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


# ── Excepción pública ─────────────────────────────────────────────────────────

class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


def _raise_for_status(r: httpx.Response) -> None:
    if r.is_error:
        detail = ""
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = r.text[:200]
        raise ApiError(f"HTTP {r.status_code}: {detail}", status_code=r.status_code)


# ── Cliente ───────────────────────────────────────────────────────────────

class ThdoraApiClient:
    def __init__(self, base_url: str = _API_BASE) -> None:
        self.base_url = base_url.rstrip("/")

    # ── Salud ───────────────────────────────────────────────────────────

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                r = await client.get(f"{self.base_url}/")
                return r.status_code == 200
        except httpx.RequestError:
            return False

    # ── Citas ───────────────────────────────────────────────────────────

    async def get_appointments(self, date_str: str) -> List[Dict[str, Any]]:
        return await self._get(f"/appointments/{date_str}")

    async def create_appointment(
        self, date_str: str, time: str, name: str, apt_type: str, notes: str = ""
    ) -> Dict[str, Any]:
        return await self._post(
            f"/appointments/{date_str}",
            json={"time": time, "name": name, "type": apt_type, "notes": notes},
        )

    async def delete_appointment(self, date_str: str, index: int) -> bool:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(f"{self.base_url}/appointments/{date_str}/{index}")
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red DELETE appointment: {exc}") from exc

    async def update_appointment(
        self, date_str: str, index: int,
        time: Optional[str] = None, name: Optional[str] = None,
        apt_type: Optional[str] = None, notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if time is not None:     payload["time"] = time
        if name is not None:     payload["name"] = name
        if apt_type is not None: payload["type"] = apt_type
        if notes is not None:    payload["notes"] = notes
        return await self._put(f"/appointments/{date_str}/{index}", json=payload)

    async def check_appointment_conflict(self, date_str: str, time: str) -> Optional[Dict[str, Any]]:
        """
        Comprueba si ya existe una cita a esa hora.
        Devuelve la cita existente (dict) o None si no hay conflicto.
        No lanza ApiError si no encuentra (404).
        """
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.get(
                    f"{self.base_url}/appointments/{date_str}/conflict/{time.replace(':', '%3A')}"
                )
                if r.status_code == 404:
                    return None
                if r.status_code == 200:
                    return r.json()
                return None
        except Exception:
            return None

    # ── Hábitos ───────────────────────────────────────────────────────────

    async def get_habits(self, date_str: str) -> Dict[str, str]:
        raw: List[Dict[str, str]] = await self._get(f"/habits/{date_str}")
        return {item["habit"]: item["value"] for item in raw}

    async def log_habit(self, date_str: str, habit: str, value: str) -> bool:
        await self._post(f"/habits/{date_str}", json={"habit": habit, "value": value})
        return True

    async def delete_habit(self, date_str: str, habit: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(f"{self.base_url}/habits/{date_str}/{habit}")
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red DELETE habit: {exc}") from exc

    async def update_habit(self, date_str: str, habit: str, value: str) -> Dict[str, str]:
        return await self._put(f"/habits/{date_str}/{habit}", json={"value": value})

    # ── HabitConfig (F9.2) ────────────────────────────────────────────────────

    async def get_habit_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Devuelve la config de un hábito o None si no existe."""
        try:
            return await self._get(f"/habit-config/{name}")
        except ApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_all_habit_configs(self) -> List[Dict[str, Any]]:
        """Lista la config de todos los hábitos."""
        return await self._get("/habit-config/")

    async def upsert_habit_config(
        self, name: str, habit_type: str = "text",
        unit: Optional[str] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        quick_vals: Optional[List[str]] = None,
        xp_rule: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Crea o actualiza la configuración de un hábito."""
        return await self._post("/habit-config/", json={
            "name": name,
            "habit_type": habit_type,
            "unit": unit,
            "min_val": min_val,
            "max_val": max_val,
            "quick_vals": quick_vals,
            "xp_rule": xp_rule,
        })

    async def delete_habit_config(self, name: str) -> bool:
        """Borra la configuración de un hábito."""
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.delete(f"{self.base_url}/habit-config/{name}")
                if r.status_code == 404:
                    return False
                _raise_for_status(r)
                return True
        except httpx.RequestError as exc:
            raise ApiError(f"Error de red DELETE habit-config: {exc}") from exc

    # ── Resumen ───────────────────────────────────────────────────────────

    async def get_summary(self, date_str: str) -> Dict[str, Any]:
        return await self._get(f"/summary/{date_str}")

    # ── Internals ───────────────────────────────────────────────────────────

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
