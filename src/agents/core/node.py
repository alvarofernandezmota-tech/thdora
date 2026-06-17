"""
Nodos del grafo LangGraph.

Cada función aquí es un "nodo" del grafo: recibe el estado actual
y devuelve un diccionario con los campos a actualizar en el estado.

Nodo principal: agent_node (razona, decide si usar tools).
"""
from __future__ import annotations
import logging
from datetime import datetime
from langchain_groq import ChatGroq
from src.agents.config import agent_config
from src.agents.core.state import ThdoraState
from src.agents.memory.manager import memory_manager
from src.agents.prompts.base import get_system_prompt
from src.agents.tools.registry import get_all_tools
from src.config import settings

logger = logging.getLogger(__name__)

_tools = get_all_tools()


def _get_llm_with_tools() -> ChatGroq:
    """Construye el LLM con tools bindeadas (lazy, una vez por proceso)."""
    llm = ChatGroq(
        model=agent_config.default_model,
        temperature=agent_config.temperature,
        max_tokens=agent_config.max_tokens,
        api_key=settings.GROQ_API_KEY,
    )
    return llm.bind_tools(_tools)


async def agent_node(state: ThdoraState) -> dict:
    """
    Nodo principal del agente: razona y decide si usar tools.

    Flujo:
        1. Recupera memoria del usuario (long_term + perfil).
        2. Construye system prompt dinámico.
        3. Invoca el LLM con historial + tools disponibles.
        4. Retorna respuesta + metadata de trazabilidad.

    Args:
        state: Estado actual del grafo (ThdoraState).

    Returns:
        Dict con nuevos mensajes y metadata actualizada.
    """
    memory = memory_manager.get_memory(state["user_id"])
    system_prompt = get_system_prompt(
        user_name=state.get("user_name") or memory.get("user_name"),
        context_summary=state.get("context_summary", ""),
        long_term_memory=memory.get("long_term_memory", ""),
    )
    messages = [{"role": "system", "content": system_prompt}] + list(state["messages"])
    llm_with_tools = _get_llm_with_tools()
    response = await llm_with_tools.ainvoke(messages)
    tool_calls_count = len(response.tool_calls) if hasattr(response, "tool_calls") and response.tool_calls else 0
    logger.debug("agent_node user_id=%s tool_calls=%s", state["user_id"], tool_calls_count)
    return {
        "messages": [response],
        "metadata": {
            "model": agent_config.default_model,
            "timestamp": datetime.now().isoformat(),
            "tool_calls": tool_calls_count,
        },
    }
