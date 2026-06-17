"""
Estado tipado del grafo LangGraph (ThdoraState).

Define la estructura de datos que fluye entre los nodos del agente.
Annotated + add_messages garantiza que LangGraph acumule mensajes correctamente.
"""
from __future__ import annotations
from typing import Annotated, Any, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ThdoraState(TypedDict):
    """
    Estado principal del agente THDORA.

    Campos:
        messages: Historial de la conversación (acumulado automáticamente).
        user_id: ID Telegram del usuario.
        user_name: Nombre del usuario (opcional, para prompts personalizados).
        context_summary: Resumen del día (citas y hábitos de hoy).
        long_term_memory: Memoria histórica persistente (resumen generado por LLM).
        pending_action: Acción pendiente para flujos multi-turno.
        metadata: Info de debugging y trazabilidad (modelo, timestamp, tool_calls).
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: int
    user_name: str | None
    context_summary: str
    long_term_memory: str
    pending_action: dict[str, Any] | None
    metadata: dict[str, Any]
