"""
Tools de citas para el agente THDORA.

Cada función decorada con @tool es una herramienta que el LLM puede invocar.
El docstring de cada tool es usado por el LLM para decidir cuándo usarla.
"""
from __future__ import annotations
import logging
from langchain_core.tools import tool
from src.bot.api_client import ThdoraApiClient

logger = logging.getLogger(__name__)
_api = ThdoraApiClient()


@tool
async def crear_cita(
    user_id: int,
    nombre: str,
    fecha: str,
    hora: str | None = None,
    tipo: str = "personal",
) -> str:
    """
    Crea una nueva cita en la agenda del usuario.

    Args:
        user_id: ID Telegram del usuario.
        nombre: Título o descripción de la cita.
        fecha: Fecha en formato YYYY-MM-DD.
        hora: Hora en formato HH:MM (opcional).
        tipo: Tipo de cita: 'personal', 'medico', 'trabajo', etc.
    """
    try:
        await _api.create_appointment(user_id, nombre, fecha, hora, tipo)
        msg = f"✅ Cita '{nombre}' creada para {fecha}"
        return msg + (f" a las {hora}." if hora else ".")
    except Exception as exc:
        logger.error("crear_cita user_id=%s: %s", user_id, exc)
        return f"❌ No pude crear la cita: {exc}"


@tool
async def consultar_citas(user_id: int, fecha: str) -> str:
    """
    Consulta las citas del usuario para una fecha concreta.

    Args:
        user_id: ID Telegram del usuario.
        fecha: Fecha en formato YYYY-MM-DD.
    """
    try:
        citas = await _api.get_appointments(user_id, fecha)
        if not citas:
            return f"📅 No tienes citas para {fecha}."
        lineas = "\n".join(
            f"  • {c.get('hora', '??:??')} — {c.get('titulo') or c.get('descripcion', 'Cita')}"
            for c in sorted(citas, key=lambda x: x.get("hora", ""))
        )
        return f"📅 Citas para {fecha}:\n{lineas}"
    except Exception as exc:
        logger.error("consultar_citas user_id=%s: %s", user_id, exc)
        return f"❌ No pude consultar: {exc}"


@tool
async def borrar_cita(user_id: int, cita_id: int) -> str:
    """
    Elimina una cita existente por su ID numérico.

    Args:
        user_id: ID Telegram del usuario.
        cita_id: ID numérico de la cita a eliminar.
    """
    try:
        await _api.delete_appointment(user_id, cita_id)
        return f"🗑️ Cita #{cita_id} eliminada correctamente."
    except Exception as exc:
        logger.error("borrar_cita user_id=%s cita_id=%s: %s", user_id, cita_id, exc)
        return f"❌ No pude eliminar la cita: {exc}"
