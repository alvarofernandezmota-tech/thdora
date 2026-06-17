"""
Tools de hábitos para el agente THDORA.
"""
from __future__ import annotations
import logging
from langchain_core.tools import tool
from src.bot.api_client import ThdoraApiClient

logger = logging.getLogger(__name__)
_api = ThdoraApiClient()


@tool
async def registrar_habito(
    user_id: int,
    habito: str,
    fecha: str,
    valor: float | None = None,
) -> str:
    """
    Registra el cumplimiento de un hábito para una fecha.

    Args:
        user_id: ID Telegram del usuario.
        habito: Nombre del hábito a registrar.
        fecha: Fecha en formato YYYY-MM-DD.
        valor: Valor numérico opcional (ej. minutos de ejercicio).
    """
    try:
        await _api.log_habit(user_id, habito, fecha, valor)
        return f"💪 Hábito '{habito}' registrado para {fecha}."
    except Exception as exc:
        logger.error("registrar_habito user_id=%s: %s", user_id, exc)
        return f"❌ No pude registrar el hábito: {exc}"
