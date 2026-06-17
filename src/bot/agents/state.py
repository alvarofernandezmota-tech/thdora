"""Estado del agente THDORA para LangGraph."""
from __future__ import annotations
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ThdoraState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: int
    nombre_usuario: str | None
    context_summary: str
    last_appointments: list[dict]
    last_habits: list[dict]
