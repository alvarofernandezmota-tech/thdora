"""
Construcción del Grafo LangGraph principal (build_thdora_graph).

Este es el corazón del sistema de agentes. Define el flujo ReAct:
    START → agent → (tools → agent)* → END

El grafo se compila con SqliteSaver como checkpointer para memoria
persistente por usuario (thread_id = user_id de Telegram).
"""
from __future__ import annotations
import logging
from functools import lru_cache
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from src.agents.core.node import _tools, agent_node
from src.agents.core.state import ThdoraState
from src.agents.memory.manager import memory_manager

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def build_thdora_graph():
    """
    Construye y compila el grafo del agente THDORA.

    Cacheado con lru_cache: se construye UNA sola vez al arrancar el bot.
    Usar build_thdora_graph() desde cualquier punto devuelve siempre la misma instancia.

    Flujo del grafo:
        START → agent_node
        agent_node → tools_node  (si el LLM llamó tools)
        tools_node → agent_node  (ciclo ReAct: observa resultados y sigue razonando)
        agent_node → END         (si el LLM no llama tools: respuesta final)

    Returns:
        CompiledGraph listo para .ainvoke(inputs, config={"configurable": {"thread_id": str(user_id)}})
    """
    workflow = StateGraph(ThdoraState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(_tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    graph = workflow.compile(checkpointer=memory_manager.checkpointer)
    logger.info("🧠 ThdoraGraph compilado (modelo=%s)", "agent_config.default_model")
    return graph
