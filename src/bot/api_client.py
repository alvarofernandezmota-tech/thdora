"""Cliente HTTP para la API FastAPI de thdora con soporte multiusuario."""

from __future__ import annotations

import logging
import os

import httpx
from telegram import Update

logger = logging.getLogger(__name__)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


def get_user_id(update: Update) -> int:
    """Extrae el Telegram user ID del Update con fallback a 0."""
    if update.effective_user is not None:
        return update.effective_user.id
    return 0


class ApiClient:
    """Cliente HTTP para la API FastAPI de thdora."""

    def __init__(self, base_url: str = API_BASE) -> None:
        self.base_url = base_url.rstrip("/")

    async def get_appointments(self, fecha: str, user_id: int = 0) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/appointments", params={"fecha": fecha, "user_id": user_id})
            resp.raise_for_status()
            return resp.json()

    async def get_appointments_range(self, fecha_inicio: str, fecha_fin: str, user_id: int = 0) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/appointments",
                params={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "user_id": user_id},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_habits(self, fecha: str | None = None, user_id: int = 0, solo_activos: bool = False) -> list[dict]:
        params: dict = {"user_id": user_id}
        if fecha:
            params["fecha"] = fecha
        if solo_activos:
            params["solo_activos"] = True
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/habits", params=params)
            resp.raise_for_status()
            return resp.json()
