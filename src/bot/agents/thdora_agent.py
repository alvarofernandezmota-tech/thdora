"""Agente principal THDORA con LangGraph — ReAct: Think → Act → Observe."""
from __future__ import annotations
import logging
from functools import lru_cache
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from src.bot.agents.prompts import SYSTEM_PROMPT
from src.bot.agents.state import ThdoraState
from src.bot.agents.tools import TOOLS
from src.config import settings

logger = logging.getLogger(__name__)


async def _agent_node(state: ThdoraState):
    """Nodo principal: llama al LLM con herramientas y contexto de usuario."""
    llm = ChatGroq(model=settings.GROQ_MODEL, temperature=0.1, api_key=settings.GROQ_API_KEY)
    llm_with_tools = llm.bind_tools(TOOLS)

    system_content = SYSTEM_PROMPT
    if state.get("context_summary"):
        system_content += f"\n\nCONTEXTO USUARIO:\n{state['context_summary']}"
    if state.get("last_appointments"):
        system_content += f"\n\nCITAS HOY: {state['last_appointments']}"
    if state.get("last_habits"):
        system_content += f"\n\nHÁBITOS RECIENTES: {state['last_habits']}"

    messages = [{"role": "system", "content": system_content}] + list(state["messages"])
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


@lru_cache(maxsize=1)
def build_thdora_graph():
    """Construye y compila el grafo LangGraph. Cacheado (singleton)."""
    workflow = StateGraph(ThdoraState)
    workflow.add_node("agent", _agent_node)
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")  # ciclo ReAct
    graph = workflow.compile()
    logger.info("🧠 LangGraph ThdoraAgent compilado")
    return graph
