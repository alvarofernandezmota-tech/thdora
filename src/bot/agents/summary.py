"""Generación automática de resúmenes de memoria para THDORA."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
from langchain_groq import ChatGroq
from src.config import settings

logger = logging.getLogger(__name__)

_llm_summary = ChatGroq(
    model=settings.GROQ_MODEL,
    temperature=0.2,
    max_tokens=800,
    api_key=settings.GROQ_API_KEY,
)


async def generate_conversation_summary(messages: list[dict], user_name: str) -> str:
    """Genera resumen conciso de los últimos mensajes."""
    if not messages:
        return "Sin interacciones recientes."
    conversation_text = "\n".join(
        f"Usuario: {m['content']}" if m.get("role") == "user" else f"THDORA: {m['content']}"
        for m in messages[-30:]
    )
    prompt = (
        f"Eres un asistente que genera resúmenes de memoria para {user_name}.\n"
        "Genera un resumen claro (máximo 400 palabras) que capture:\n"
        "- Objetivos y prioridades del usuario\n"
        "- Hábitos y rutinas mencionadas\n"
        "- Información importante (preferencias, proyectos, etc.)\n"
        "- Logros o eventos relevantes\n\n"
        f"Conversación reciente:\n{conversation_text}\n\nResumen:"
    )
    response = await _llm_summary.ainvoke(prompt)
    return response.content.strip()


async def update_long_term_memory(user_id: int, new_summary: str) -> None:
    """Combina resumen nuevo con memoria anterior y guarda en UserConfig."""
    try:
        from src.db.models import UserConfig
        from src.db.session import get_db
        with get_db() as db:
            config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
            if config:
                current = getattr(config, "long_term_memory", "") or ""
                date_str = datetime.now().strftime("%Y-%m-%d")
                combined = f"{current}\n\n--- Actualizado {date_str} ---\n{new_summary}"
                config.long_term_memory = combined[-2000:] if len(combined) > 2000 else combined
                db.commit()
    except Exception as exc:
        logger.error("update_long_term_memory user_id=%s: %s", user_id, exc)


async def get_user_recent_messages(user_id: int) -> list[dict[str, Any]]:
    """Obtiene mensajes recientes del usuario desde la tabla MessageLog (TODO: implementar)."""
    # Placeholder — implementar con tabla MessageLog en Sprint 6
    return []
