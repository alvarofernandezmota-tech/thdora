import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport

from tools.registry import ToolRegistry


@pytest.fixture
def agent_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_groq_response():
    from langchain_core.messages import AIMessage
    return {"messages": [AIMessage(content="Hola, soy THDORA.")]}


@pytest.mark.asyncio
async def test_chat_returns_reply(agent_id, mock_groq_response):
    from agents.orchestrator import AgentOrchestrator

    with patch("agents.orchestrator.create_react_agent") as mock_create_graph:
        mock_graph = AsyncMock()
        mock_graph.ainvoke = AsyncMock(return_value=mock_groq_response)
        mock_create_graph.return_value = mock_graph

        with patch("agents.orchestrator.ChatGroq"):
            orc = AgentOrchestrator(
                agent_id=agent_id,
                system_prompt="Eres un asistente.",
                tools_config=[],
                model="llama-3.3-70b-versatile",
            )
            orc._graph = mock_graph

            reply = await orc.chat(
                user_message="Hola",
                chat_id="test-chat",
                history=[],
                db=None,
            )

    assert reply == "Hola, soy THDORA."


def test_tool_registry_load():
    registry = ToolRegistry()

    valid_schema = {
        "type": "object",
        "properties": {"date": {"type": "string"}},
    }
    registry.register(
        name="get_appointments",
        description="Obtiene citas",
        json_schema=valid_schema,
    )

    assert registry.get("get_appointments") is not None
    assert registry.get("get_appointments")["name"] == "get_appointments"
    assert len(registry.all()) == 1

    invalid_schema = {"type": 12345}
    with pytest.raises(ValueError, match="Invalid JSON Schema"):
        registry.register(
            name="bad_tool",
            description="Tool con schema roto",
            json_schema=invalid_schema,
        )

    assert registry.get("bad_tool") is None


@pytest.mark.asyncio
async def test_auth_missing_key():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../platform"))
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/agents/")
        assert response.status_code == 401

        response = await client.get("/agents/", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401
