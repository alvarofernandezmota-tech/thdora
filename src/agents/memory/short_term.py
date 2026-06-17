"""
Memoria a corto plazo: contexto de sesión.

Gestiona el historial reciente de la conversación activa.
Este contexto se inyecta en el state de LangGraph como 'context_summary'.

Nota: LangGraph con SqliteSaver ya persiste messages por thread_id.
Este módulo es para contexto adicional (citas hoy, hábitos, etc.).
"""
from __future__ import annotations
import logging
from src.bot.api_client import ThdoraApiClient

logger = logging.getLogger(__name__)
_api = ThdoraApiClient()


async def build_context_summary(user_id: int, fecha_hoy: str) -> str:
    """
    Construye un resumen del día del usuario para inyectar como contexto.

    Consulta citas y hábitos de hoy via API y genera un texto conciso.

    Args:
        user_id: ID Telegram del usuario.
        fecha_hoy: Fecha en formato YYYY-MM-DD.

    Returns:
        Texto con resumen del día (citas + hábitos).
    """
    parts: list[str] = []
    try:
        citas = await _api.get_appointments(user_id, fecha_hoy)
        if citas:
            lineas = ", ".join(
                f"{c.get('hora', '?')} {c.get('titulo') or c.get('descripcion', 'Cita')}"
                for c in sorted(citas, key=lambda x: x.get("hora", ""))
            )
            parts.append(f"Citas hoy: {lineas}")
    except Exception as exc:
        logger.warning("build_context_summary citas user_id=%s: %s", user_id, exc)
    return "\n".join(parts) if parts else ""
