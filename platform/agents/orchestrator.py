"""LangGraph Orchestrator — carga agente por UUID y ejecuta tool calling dinámico."""
from __future__ import annotations
import importlib
import json
from typing import Annotated, Any
from uuid import UUID

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from core.config import settings
from core.cache import get_cached_agent_config, cache_agent_config


# ── Estado del grafo ─────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    agent_config: dict
    tool_calls_made: list[str]


# ── Carga dinámica de tools ───────────────────────────────────
def load_tool_function(implementation_ref: str):
    """Importa dinámicamente la función de implementación de un tool.
    Formato: 'module.submodule.function'
    """
    *module_parts, func_name = implementation_ref.split(".")
    module = importlib.import_module(".".join(module_parts))
    return getattr(module, func_name)


def build_langchain_tool(tool_config: dict):
    """Convierte un tool del registry en un LangChain tool callable."""
    from langchain_core.tools import tool as lc_tool

    impl_ref = tool_config.get("implementation_ref")
    schema = tool_config["json_schema"]
    name = tool_config["name"]
    description = tool_config["description"]

    if impl_ref:
        try:
            impl_fn = load_tool_function(impl_ref)
        except (ImportError, AttributeError):
            impl_fn = None
    else:
        impl_fn = None

    @lc_tool(name=name, description=description)
    def dynamic_tool(**kwargs: Any) -> str:
        if impl_fn:
            return str(impl_fn(**kwargs))
        return f"[Tool {name} ejecutado con args: {json.dumps(kwargs)}]"

    return dynamic_tool


# ── Orquestador principal ─────────────────────────────────────
class AgentOrchestrator:
    """Carga un agente por su UUID, construye el grafo LangGraph y ejecuta."""

    def __init__(self, agent_config: dict, tools_config: list[dict]):
        self.config = agent_config
        self.tools_config = tools_config
        self.tools = [build_langchain_tool(t) for t in tools_config]
        self.llm = self._build_llm()
        self.graph = self._build_graph()

    def _build_llm(self):
        model = self.config.get("model", settings.default_model)
        temperature = self.config.get("temperature", 0.7)

        if settings.groq_api_key:
            llm = ChatGroq(
                model=model,
                temperature=temperature,
                api_key=settings.groq_api_key,
            )
        else:
            llm = Ollama(model=model, temperature=temperature)

        if self.tools:
            llm = llm.bind_tools(self.tools)
        return llm

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", self._tools_node)

        graph.set_entry_point("agent")
        graph.add_conditional_edges("agent", self._should_use_tools)
        graph.add_edge("tools", "agent")

        return graph.compile()

    def _agent_node(self, state: AgentState) -> dict:
        system_prompt = self.config.get("system_prompt", "Eres un asistente útil.")
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def _tools_node(self, state: AgentState) -> dict:
        """Ejecuta los tool calls que pidió el LLM."""
        from langchain_core.messages import ToolMessage
        last_message = state["messages"][-1]
        tool_calls_made = state.get("tool_calls_made", [])
        results = []

        tool_map = {t.name: t for t in self.tools}

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_fn = tool_map.get(tool_name)
            if tool_fn:
                result = tool_fn.invoke(tool_call["args"])
                tool_calls_made.append(tool_name)
            else:
                result = f"Tool '{tool_name}' no encontrado en registry."

            results.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

        return {"messages": results, "tool_calls_made": tool_calls_made}

    def _should_use_tools(self, state: AgentState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    async def chat(self, message: str, chat_id: str, history: list[dict] = None) -> dict:
        """Punto de entrada principal para un mensaje."""
        messages = []
        if history:
            from langchain_core.messages import AIMessage
            for h in history[-10:]:  # últimos 10 mensajes de contexto
                if h["role"] == "user":
                    messages.append(HumanMessage(content=h["content"]))
                elif h["role"] == "assistant":
                    messages.append(AIMessage(content=h["content"]))

        messages.append(HumanMessage(content=message))

        initial_state: AgentState = {
            "messages": messages,
            "agent_config": self.config,
            "tool_calls_made": [],
        }

        final_state = await self.graph.ainvoke(initial_state)
        last_message = final_state["messages"][-1]

        return {
            "reply": last_message.content,
            "tool_calls_made": final_state.get("tool_calls_made", []),
        }


# ── Factory helper ────────────────────────────────────────────
async def get_orchestrator(agent_id: str, db_session) -> AgentOrchestrator:
    """Carga config del agente (Redis caché → BD) y devuelve orquestador listo."""
    from agents.crud import get_agent_with_tools

    cached = await get_cached_agent_config(agent_id)
    if cached:
        agent_data = cached["agent"]
        tools_data = cached["tools"]
    else:
        agent_data, tools_data = await get_agent_with_tools(db_session, UUID(agent_id))
        await cache_agent_config(agent_id, {"agent": agent_data, "tools": tools_data})

    return AgentOrchestrator(agent_config=agent_data, tools_config=tools_data)
