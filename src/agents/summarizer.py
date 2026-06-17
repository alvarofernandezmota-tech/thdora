"""
Generador de resúmenes de conversación.

Usa el LLM para comprimir el historial de mensajes en un resumen
que se guarda como long_term_memory del usuario.

Llamado desde scheduler_tasks.py cada noche a las 23:00.
"""
from __future__ import annotations
import logging
from langchain_groq import ChatGroq
from src.agents.config import agent_config
from src.agents.prompts.templates import SUMMARY_PROMPT
from src.config import settings

logger = logging.getLogger(__name__)

_llm = ChatGroq(
    model=agent_config.default_model,
    temperature=0.2,
    max_tokens=800,
    api_key=settings.GROQ_API_KEY,
)


async def generate_conversation_summary(messages: list[dict], user_name: str) -> str:
    """
    Genera un resumen conciso del historial de mensajes del usuario.

    Args:
        messages: Lista de dicts con 'role' y 'content'.
        user_name: Nombre del usuario para personalizar el prompt.

    Returns:
        Resumen en texto plano (máx. 400 palabras).
    """
    if not messages:
        return ""
    conversation_text = "\n".join(
        f"Usuario: {m['content']}" if m.get("role") == "user" else f"THDORA: {m['content']}"
        for m in messages[-30:]
    )
    prompt = SUMMARY_PROMPT.format(user_name=user_name, conversation_text=conversation_text)
    response = await _llm.ainvoke(prompt)
    return response.content.strip()
