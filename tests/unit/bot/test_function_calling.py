"""Tests de function calling (tool_calls) en GroqRouter."""

from __future__ import annotations
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

os.environ.setdefault("GROQ_API_KEY", "test_key")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")

from src.bot.groq_router import AmbiguityRequest, GroqRouter, ToolCallResult, TOOLS


def _groq_response_with_tool(func_name, arguments):
    return {"choices": [{"message": {"content": None, "tool_calls": [{"id": "call_abc", "type": "function", "function": {"name": func_name, "arguments": json.dumps(arguments)}}]}}]}


def _groq_response_conversacional(text):
    return {"choices": [{"message": {"content": json.dumps({"intent": "consulta_general", "accion": None, "entidades": {}, "respuesta_usuario": text}), "tool_calls": None}}]}


def _mock_httpx(json_body):
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_body
    mock_resp.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


@pytest.mark.asyncio
async def test_tool_call_crear_cita_complete() -> None:
    router = GroqRouter()
    args = {"nombre": "Dentista", "fecha": "2025-06-20", "hora": "10:00", "tipo": "médica"}
    with patch("httpx.AsyncClient", return_value=_mock_httpx(_groq_response_with_tool("crear_cita", args))):
        result = await router.process("Cita con el dentista el viernes a las 10")
    assert isinstance(result, ToolCallResult)
    assert result.action == "crear_cita"
    assert result.success is True
    assert "Dentista" in result.message_to_user


@pytest.mark.asyncio
async def test_tool_call_missing_hora() -> None:
    router = GroqRouter()
    args = {"nombre": "Dentista", "fecha": "2025-06-20"}
    with patch("httpx.AsyncClient", return_value=_mock_httpx(_groq_response_with_tool("crear_cita", args))):
        result = await router.process("Cita con el dentista el viernes")
    assert isinstance(result, AmbiguityRequest)
    assert "hora" in result.missing_fields


@pytest.mark.asyncio
async def test_tool_call_borrar_cita() -> None:
    router = GroqRouter()
    args = {"cita_id": 7}
    with patch("httpx.AsyncClient", return_value=_mock_httpx(_groq_response_with_tool("borrar_cita", args))):
        result = await router.process("Borra la cita número 7")
    assert isinstance(result, ToolCallResult)
    assert result.action == "borrar_cita"
    assert result.data["cita_id"] == 7


@pytest.mark.asyncio
async def test_no_tool_call_conversacional() -> None:
    router = GroqRouter()
    with patch("httpx.AsyncClient", return_value=_mock_httpx(_groq_response_conversacional("Hola, ¿en qué te ayudo?"))):
        result = await router.process("Hola")
    assert isinstance(result, str)
    assert "Hola" in result or "ayudo" in result


def test_tool_schema_valid_json() -> None:
    parsed = json.loads(json.dumps(TOOLS))
    assert len(parsed) == 3
    nombres = {t["function"]["name"] for t in parsed}
    assert nombres == {"crear_cita", "borrar_cita", "consultar_citas"}
