"""
Grafo principal LangGraph de THDORA.

Define el flujo de razonamiento del agente:
  START → agent_node → [tools_condition] → tools / END

Uso:
    from src.agents.core.graph import build_thdora_graph
    graph = build_thdora_graph()
    result = await graph.ainvoke(state, config={"configurable": {"thread_id": str(user_id)}})
"""
import logging
from functools import lru_cache
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from src.agents.core.node import _get_tools, agent_node
from src.agents.core.state import ThdoraState
from src.agents.memory.manager import memory_manager

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def build_thdora_graph():
    """
    Construye y compila el grafo LangGraph de THDORA.

    Nodos:
        - agent: razona y decide si usar herramientas.
        - tools: ejecuta las herramientas seleccionadas.

    Edges:
        START → agent → tools (si hay tool_calls) / END
        tools → agent (loop hasta que el agente no pida más tools)

    Returns:
        CompiledGraph listo para ainvoke().
    """
    workflow = StateGraph(ThdoraState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(_get_tools()))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    return workflow.compile(checkpointer=memory_manager.checkpointer)
