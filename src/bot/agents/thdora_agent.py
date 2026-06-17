"""Agente principal THDORA con LangGraph + SqliteSaver (memoria persistente) — v0.20.1."""
from __future__ import annotations
import logging
from functools import lru_cache
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from src.bot.agents.prompts import get_system_prompt
from src.bot.agents.memory import thdora_memory
from src.bot.agents.state import ThdoraState
from src.bot.agents.tools import TOOLS
from src.config import settings

logger = logging.getLogger(__name__)


async def _agent_node(state: ThdoraState):
    """Nodo LLM: inyecta perfil + contexto dinámico + llama al modelo con tools."""
    user_memory = thdora_memory.get_user_memory(state["user_id"])
    system_prompt = get_system_prompt(
        nombre=state.get("nombre_usuario") or user_memory["profile"].get("nombre"),
        context_summary=state.get("context_summary", ""),
        long_term=user_memory.get("summary", ""),
    )
    llm = ChatGroq(model=settings.GROQ_MODEL, temperature=0.1, api_key=settings.GROQ_API_KEY)
    llm_with_tools = llm.bind_tools(TOOLS)
    messages = [{"role": "system", "content": system_prompt}] + list(state["messages"])
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


@lru_cache(maxsize=1)
def build_thdora_graph():
    """Construye y compila el grafo con SqliteSaver (checkpoint por thread_id=user_id)."""
    from langgraph.checkpoint.sqlite import SqliteSaver
    checkpointer = SqliteSaver.from_conn_string("data/thdora_memory.db")

    workflow = StateGraph(ThdoraState)
    workflow.add_node("agent", _agent_node)
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")  # ciclo ReAct

    graph = workflow.compile(checkpointer=checkpointer)
    logger.info("🧠 LangGraph ThdoraAgent compilado con SqliteSaver")
    return graph
