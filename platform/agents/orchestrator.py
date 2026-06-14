import uuid
import json
import logging
from typing import Any, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool as lc_tool
from langgraph.prebuilt import create_react_agent
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from agents.models import MessageRole
from agents import crud

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orquestador LangGraph para un agente concreto."""

    def __init__(
        self,
        agent_id: uuid.UUID,
        system_prompt: str,
        tools_config: list[dict],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> None:
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self.tools_config = tools_config
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self._llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self._lc_tools = self._build_lc_tools(tools_config)
        self._graph = create_react_agent(self._llm, tools=self._lc_tools)

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _build_lc_tools(tools_config: list[dict]):
        """Convierte la config de tools en callables LangChain."""
        lc_tools = []
        for tc in tools_config:
            name = tc["name"]
            description = tc.get("description", "")
            impl = tc.get("_impl")

            if impl is not None:
                decorated = lc_tool(name=name, description=description)(impl)
            else:
                async def _stub(**kwargs: Any) -> str:
                    return json.dumps({"error": f"Tool '{name}' has no implementation."})
                decorated = lc_tool(name=name, description=description)(_stub)

            lc_tools.append(decorated)
        return lc_tools

    @staticmethod
    def _history_to_lc(history: list[dict]) -> list[BaseMessage]:
        mapping = {"user": HumanMessage, "assistant": AIMessage}
        messages: list[BaseMessage] = []
        for entry in history:
            cls = mapping.get(entry["role"])
            if cls:
                messages.append(cls(content=entry["content"]))
        return messages

    # ── Public API ────────────────────────────────────────────────────────────

    async def chat(
        self,
        user_message: str,
        chat_id: str = "default",
        history: Optional[list[dict]] = None,
        db: Optional[AsyncSession] = None,
    ) -> str:
        if history is None:
            if db is not None:
                history = await crud.get_history(db, self.agent_id, chat_id)
            else:
                history = []

        lc_history = self._history_to_lc(history)
        all_messages: list[BaseMessage] = (
            [SystemMessage(content=self.system_prompt)]
            + lc_history
            + [HumanMessage(content=user_message)]
        )

        result = await self._graph.ainvoke({"messages": all_messages})
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        reply: str = ai_messages[-1].content if ai_messages else ""

        if db is not None:
            await crud.save_message(
                db, self.agent_id, chat_id, MessageRole.user, user_message
            )
            await crud.save_message(
                db, self.agent_id, chat_id, MessageRole.assistant, reply
            )

        return reply


# ── Cache de orquestadores ────────────────────────────────────────────────────

_orchestrator_cache: dict[str, AgentOrchestrator] = {}


async def get_orchestrator(
    agent_id: uuid.UUID,
    db: AsyncSession,
    redis_client=None,
) -> AgentOrchestrator | None:
    cache_key = str(agent_id)

    if cache_key in _orchestrator_cache:
        return _orchestrator_cache[cache_key]

    if redis_client is not None:
        cached = await redis_client.get(f"orchestrator:{cache_key}")
        if cached:
            data = json.loads(cached)
            orc = AgentOrchestrator(**data)
            _orchestrator_cache[cache_key] = orc
            return orc

    agent, tools = await crud.get_agent_with_tools(db, agent_id)
    if agent is None:
        return None

    tools_config = [
        {
            "name": t.name,
            "description": t.description,
            "json_schema": t.json_schema,
        }
        for t in tools
    ]

    orc = AgentOrchestrator(
        agent_id=agent.id,
        system_prompt=agent.system_prompt,
        tools_config=tools_config,
        model=agent.model,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
    )
    _orchestrator_cache[cache_key] = orc

    if redis_client is not None:
        payload = json.dumps(
            {
                "agent_id": str(agent.id),
                "system_prompt": agent.system_prompt,
                "tools_config": tools_config,
                "model": agent.model,
                "temperature": agent.temperature,
                "max_tokens": agent.max_tokens,
            }
        )
        await redis_client.setex(
            f"orchestrator:{cache_key}", settings.redis_agent_cache_ttl, payload
        )

    return orc


def invalidate_orchestrator_cache(agent_id: uuid.UUID) -> None:
    _orchestrator_cache.pop(str(agent_id), None)
