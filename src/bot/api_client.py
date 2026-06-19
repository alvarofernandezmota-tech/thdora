"""Cliente HTTP asíncrono para la API FastAPI de THDORA — v5 con lazy base_url."""
from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)


def _get_api_base() -> str:
    """Lee THDORA_API_URL lazy (solo cuando se instancia el cliente)."""
    from src.config import settings
    return settings.THDORA_API_URL.rstrip("/")


class ApiError(Exception):
    """Excepción para errores de API."""
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.is_error:
        detail = ""
        try:
            detail = resp.json().get("detail", "")
        except Exception:
            detail = resp.text[:200]
        raise ApiError(f"HTTP {resp.status_code}: {detail}", status_code=resp.status_code)


def _validate_user_id(user_id: int) -> None:
    if not user_id or user_id <= 0:
        raise ValueError("user_id es obligatorio y debe ser > 0")


class ThdoraApiClient:
    """Cliente HTTP asíncrono para la API de THDORA con singleton pattern.

    Soporta dos formas de uso, ambas comparten la misma conexión httpx
    (almacenada a nivel de clase) para no abrir un socket por instancia:

        api = ThdoraApiClient()              # uso directo (constructor normal)
        api = await ThdoraApiClient.get_instance()  # uso explícito del singleton
    """

    _instance: ThdoraApiClient | None = None
    _client: httpx.AsyncClient | None = None

    @classmethod
    def _ensure_client(cls) -> None:
        """Crea el httpx.AsyncClient compartido si aún no existe (lazy, idempotente)."""
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                base_url=_get_api_base(),
                timeout=_TIMEOUT,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )

    @classmethod
    async def get_instance(cls) -> ThdoraApiClient:
        if cls._instance is None:
            cls._instance = cls()
        cls._ensure_client()
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        if cls._client:
            await cls._client.aclose()
            cls._client = None
            cls._instance = None

    async def _request(
        self, method: str, endpoint: str, user_id: int, **kwargs: Any
    ) -> httpx.Response:
        _validate_user_id(user_id)
        type(self)._ensure_client()  # garantiza _client aunque se use constructor directo
        params = kwargs.pop("params", {})
        params["user_id"] = user_id
        resp = await self._client.request(method, endpoint, params=params, **kwargs)
        _raise_for_status(resp)
        return resp

    # ── Health ────────────────────────────────────────────────────────────────────
    async def health(self) -> bool:
        type(self)._ensure_client()
        try:
            resp = await self._client.get("/")
            return resp.status_code == 200
        except Exception:
            return False

    # ── Appointments ───────────────────────────────────────────────────────────
    async def get_appointments(self, fecha: str, user_id: int) -> list[dict]:
        resp = await self._request("GET", f"/appointments/{fecha}", user_id)
        return resp.json()

    async def get_appointments_week(self, fecha: str, user_id: int) -> dict:
        resp = await self._request("GET", f"/appointments/week/{fecha}", user_id)
        return resp.json()

    async def get_appointments_range(
        self, fecha_inicio: str, fecha_fin: str, user_id: int
    ) -> dict:
        resp = await self._request(
            "GET", f"/appointments/range/{fecha_inicio}/{fecha_fin}", user_id
        )
        return resp.json()

    async def get_upcoming(
        self, fecha: str, user_id: int, limit: int = 10
    ) -> list[dict]:
        resp = await self._request(
            "GET", f"/appointments/upcoming/{fecha}", user_id,
            params={"limit": limit},
        )
        return resp.json()

    async def create_appointment(
        self, date_str: str, data: dict, user_id: int
    ) -> dict:
        resp = await self._request(
            "POST", f"/appointments/{date_str}", user_id, json=data
        )
        return resp.json()

    async def update_appointment(
        self, date_str: str, index: int, data: dict, user_id: int
    ) -> dict:
        resp = await self._request(
            "PUT", f"/appointments/{date_str}/{index}", user_id, json=data
        )
        return resp.json()

    async def delete_appointment(
        self, date_str: str, index: int, user_id: int
    ) -> bool:
        resp = await self._request(
            "DELETE", f"/appointments/{date_str}/{index}", user_id
        )
        return resp.status_code == 204

    # ── Habits ───────────────────────────────────────────────────────────────────
    async def get_habits(self, fecha: str, user_id: int) -> list[dict]:
        resp = await self._request("GET", f"/habits/{fecha}", user_id)
        return resp.json()

    async def get_habits_week(self, fecha: str, user_id: int) -> list[dict]:
        resp = await self._request("GET", f"/habits/week/{fecha}", user_id)
        return resp.json()

    async def get_habits_range(
        self, desde: str, hasta: str, user_id: int
    ) -> list[dict]:
        resp = await self._request(
            "GET", f"/habits/range/{desde}/{hasta}", user_id
        )
        return resp.json()

    async def get_habit_stats(
        self, habit_name: str, user_id: int, days: int = 30
    ) -> list[dict]:
        resp = await self._request(
            "GET", f"/habits/stats/{habit_name}", user_id,
            params={"days": days},
        )
        return resp.json()

    async def log_habit(
        self, date_str: str, habit: str, value: str, user_id: int
    ) -> dict:
        resp = await self._request(
            "POST", f"/habits/{date_str}", user_id,
            json={"habit": habit, "value": value},
        )
        return resp.json()

    async def update_habit(
        self, date_str: str, habit: str, value: str, user_id: int
    ) -> dict:
        resp = await self._request(
            "PUT", f"/habits/{date_str}/{habit}", user_id,
            json={"value": value},
        )
        return resp.json()

    async def delete_habit(
        self, date_str: str, habit: str, user_id: int
    ) -> bool:
        resp = await self._request(
            "DELETE", f"/habits/{date_str}/{habit}", user_id
        )
        return resp.status_code == 204

    # ── Habit Config ───────────────────────────────────────────────────────────────
    async def get_habit_configs(self, user_id: int) -> list[dict]:
        resp = await self._request("GET", "/habit-config/", user_id)
        return resp.json()

    async def get_habit_config(self, name: str, user_id: int) -> dict | None:
        try:
            resp = await self._request("GET", f"/habit-config/{name}", user_id)
            return resp.json()
        except ApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def upsert_habit_config(self, data: dict, user_id: int) -> dict:
        resp = await self._request("POST", "/habit-config/", user_id, json=data)
        return resp.json()

    async def delete_habit_config(self, name: str, user_id: int) -> bool:
        resp = await self._request("DELETE", f"/habit-config/{name}", user_id)
        return resp.status_code == 204

    # ── User Config ───────────────────────────────────────────────────────────────
    async def get_user_config(self, user_id: int) -> dict:
        resp = await self._request("GET", f"/user_config/{user_id}", user_id)
        return resp.json()

    async def update_user_config(self, user_id: int, data: dict) -> dict:
        resp = await self._request(
            "PUT", f"/user_config/{user_id}", user_id, json=data
        )
        return resp.json()

    # ── Summary ──────────────────────────────────────────────────────────────────
    async def get_summary(self, fecha: str, user_id: int) -> dict:
        resp = await self._request("GET", f"/summary/{fecha}", user_id)
        return resp.json()

    async def get_summary_week(self, fecha: str, user_id: int) -> list[dict]:
        resp = await self._request("GET", f"/summary/week/{fecha}", user_id)
        return resp.json()

    # ── Conversations ───────────────────────────────────────────────────────────────
    async def save_message(
        self,
        role: str,
        content: str,
        user_id: int,
        session_id: str | None = None,
    ) -> dict:
        resp = await self._request(
            "POST", "/conversations", user_id,
            json={"role": role, "content": content, "session_id": session_id},
        )
        return resp.json()

    async def get_history(self, user_id: int, limit: int = 10) -> list[dict]:
        resp = await self._request(
            "GET", f"/conversations/{user_id}", user_id,
            params={"limit": limit},
        )
        return resp.json().get("history", [])

    async def delete_history(self, user_id: int) -> bool:
        resp = await self._request(
            "DELETE", f"/conversations/{user_id}", user_id
        )
        return resp.status_code == 204
