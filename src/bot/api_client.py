"""Cliente HTTP para la API FastAPI de thdora con soporte multiusuario."""
from __future__ import annotations

import logging

from telegram import Update

from src.bot.http_client import get_client
from src.config import settings

logger = logging.getLogger(__name__)


def get_user_id(update: Update) -> int:
    """Extrae el user_id de Telegram del update, devuelve 0 si no está disponible."""
    if update.effective_user is not None:
        return update.effective_user.id
    return 0


class ThdoraApiClient:
    """Cliente asíncrono para la API REST de THDORA."""

    def __init__(self) -> None:
        self.base_url = settings.THDORA_API_URL.rstrip("/")

    async def health(self) -> bool:
        """Comprueba si la API está disponible."""
        try:
            r = await get_client().get(f"{self.base_url}/")
            return r.status_code == 200
        except Exception:
            return False

    async def get_appointments(self, fecha: str, user_id: int = 0) -> list[dict]:
        """Devuelve las citas de un día concreto para un usuario."""
        r = await get_client().get(
            f"{self.base_url}/appointments",
            params={"fecha": fecha, "user_id": user_id},
        )
        r.raise_for_status()
        return r.json()

    async def get_appointments_range(
        self, fecha_inicio: str, fecha_fin: str, user_id: int = 0
    ) -> list[dict]:
        """Devuelve las citas en un rango de fechas para un usuario."""
        r = await get_client().get(
            f"{self.base_url}/appointments",
            params={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "user_id": user_id},
        )
        r.raise_for_status()
        return r.json()

    async def get_habits(
        self, fecha: str | None = None, user_id: int = 0, solo_activos: bool = False
    ) -> list[dict]:
        """Devuelve los hábitos del usuario, opcionalmente filtrados por fecha."""
        params: dict = {"user_id": user_id}
        if fecha:
            params["fecha"] = fecha
        if solo_activos:
            params["solo_activos"] = True
        r = await get_client().get(f"{self.base_url}/habits", params=params)
        r.raise_for_status()
        return r.json()
