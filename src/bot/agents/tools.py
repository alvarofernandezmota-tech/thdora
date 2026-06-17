"""Tools LangGraph para THDORA — wrappean ThdoraApiClient."""
from __future__ import annotations
import logging
from langchain_core.tools import tool
from src.bot.api_client import ThdoraApiClient

logger = logging.getLogger(__name__)
_api = ThdoraApiClient()


@tool
async def crear_cita(user_id: int, nombre: str, fecha: str, hora: str | None = None, tipo: str = "personal") -> str:
    """Crea una nueva cita en la agenda del usuario."""
    try:
        result = await _api.create_appointment(user_id, nombre, fecha, hora, tipo)
        return f"✅ Cita '{nombre}' creada para {fecha}" + (f" a las {hora}." if hora else ".")
    except Exception as exc:
        logger.error("crear_cita error: %s", exc)
        return f"❌ No pude crear la cita: {exc}"


@tool
async def consultar_citas(user_id: int, fecha: str) -> str:
    """Consulta las citas de una fecha concreta (YYYY-MM-DD)."""
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
        logger.error("consultar_citas error: %s", exc)
        return f"❌ No pude consultar las citas: {exc}"


@tool
async def borrar_cita(user_id: int, cita_id: int) -> str:
    """Elimina una cita existente por su ID numérico."""
    try:
        await _api.delete_appointment(user_id, cita_id)
        return f"🗑️ Cita #{cita_id} eliminada correctamente."
    except Exception as exc:
        logger.error("borrar_cita error: %s", exc)
        return f"❌ No pude eliminar la cita: {exc}"


@tool
async def registrar_habito(user_id: int, habito: str, fecha: str, valor: float | None = None) -> str:
    """Registra el cumplimiento de un hábito para una fecha."""
    try:
        await _api.log_habit(user_id, habito, fecha, valor)
        return f"💪 Hábito '{habito}' registrado para {fecha}."
    except Exception as exc:
        logger.error("registrar_habito error: %s", exc)
        return f"❌ No pude registrar el hábito: {exc}"


TOOLS = [crear_cita, consultar_citas, borrar_cita, registrar_habito]
