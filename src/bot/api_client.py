import logging
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class ThdoraApiClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient()

    # ── Health ───────────────────────────────────────────────────────────────

    async def health(self) -> bool:
        try:
            r = await self._client.get(f"{self.base_url}/health", timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    # ── Appointments ─────────────────────────────────────────────────────────

    async def get_appointments(self, user_id: int, fecha: str) -> list[dict]:
        try:
            r = await self._client.get(
                f"{self.base_url}/appointments",
                params={"user_id": user_id, "fecha": fecha},
                timeout=5.0,
            )
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else data.get("appointments", [])
        except Exception as e:
            logger.warning("get_appointments error: %s", e)
            return []

    async def get_appointments_today(self, user_id: int) -> list[dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return await self.get_appointments(user_id, today)

    async def create_appointment(self, user_id: int, payload: dict) -> dict | None:
        try:
            r = await self._client.post(
                f"{self.base_url}/appointments",
                json={"user_id": user_id, **payload},
                timeout=5.0,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning("create_appointment error: %s", e)
            return None

    async def delete_appointment(self, user_id: int, appt_id: int) -> bool:
        try:
            r = await self._client.delete(
                f"{self.base_url}/appointments/{appt_id}",
                params={"user_id": user_id},
                timeout=5.0,
            )
            return r.status_code == 204
        except Exception as e:
            logger.warning("delete_appointment error: %s", e)
            return False

    # ── Habits ───────────────────────────────────────────────────────────────

    async def get_active_habits(self, user_id: int) -> list[dict]:
        try:
            r = await self._client.get(
                f"{self.base_url}/habits",
                params={"user_id": user_id, "active": True},
                timeout=5.0,
            )
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else data.get("habits", [])
        except Exception as e:
            logger.warning("get_active_habits error: %s", e)
            return []

    async def log_habit(self, user_id: int, habit_id: int) -> bool:
        try:
            r = await self._client.post(
                f"{self.base_url}/habits/{habit_id}/log",
                json={"user_id": user_id},
                timeout=5.0,
            )
            return r.status_code in (200, 201)
        except Exception as e:
            logger.warning("log_habit error: %s", e)
            return False

    # ── Conversations (memoria persistente) ──────────────────────────────────

    async def save_message(self, user_id: int, role: str, content: str) -> None:
        try:
            await self._client.post(
                f"{self.base_url}/conversations",
                json={"user_id": user_id, "role": role, "content": content},
                timeout=3.0,
            )
        except Exception as e:
            logger.warning("save_message error: %s", e)

    async def get_history(self, user_id: int, limit: int = 5) -> list[dict]:
        try:
            r = await self._client.get(
                f"{self.base_url}/conversations/{user_id}",
                params={"limit": limit},
                timeout=3.0,
            )
            if r.status_code == 200:
                return r.json().get("history", [])
            return []
        except Exception as e:
            logger.warning("get_history error: %s", e)
            return []

    async def delete_history(self, user_id: int) -> bool:
        try:
            r = await self._client.delete(
                f"{self.base_url}/conversations/{user_id}",
                timeout=3.0,
            )
            return r.status_code == 204
        except Exception as e:
            logger.warning("delete_history error: %s", e)
            return False

    # ── Users ─────────────────────────────────────────────────────────────────

    async def get_user_name(self, user_id: int) -> str:
        try:
            r = await self._client.get(
                f"{self.base_url}/users/{user_id}/name",
                timeout=3.0,
            )
            if r.status_code == 200:
                return r.json().get("name", "Usuario")
            return "Usuario"
        except Exception:
            return "Usuario"

    # ── Events / metricas ────────────────────────────────────────────────────

    async def log_event(
        self, user_id: int, event_type: str, metadata: dict | None = None
    ) -> None:
        try:
            await self._client.post(
                f"{self.base_url}/events",
                json={"user_id": user_id, "event_type": event_type, "metadata": metadata or {}},
                timeout=3.0,
            )
        except Exception as e:
            logger.warning("log_event error: %s", e)

    async def get_stats(self, user_id: int) -> dict:
        try:
            r = await self._client.get(
                f"{self.base_url}/events/{user_id}/stats",
                timeout=5.0,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning("get_stats error: %s", e)
            return {}

    # ── Cleanup ──────────────────────────────────────────────────────────────

    async def close(self) -> None:
        await self._client.aclose()


# Alias para compatibilidad con imports que usen ApiClient
ApiClient = ThdoraApiClient
