"""Tests unitarios para src/bot/llm_backend.py."""

from __future__ import annotations
import os
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest

os.environ.setdefault("GROQ_API_KEY", "test_key")

from src.bot.llm_backend import GroqBackend, LLMBackendFactory, LLMResponse, OllamaBackend


GROQ_RESPONSE = {"choices": [{"message": {"content": "Hola desde Groq", "tool_calls": None}}]}
OLLAMA_RESPONSE = {"message": {"content": "Hola desde Ollama", "tool_calls": None}}


def _mock_client(json_body):
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_body
    mock_resp.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestGroqBackend:
    @pytest.mark.asyncio
    async def test_groq_backend_calls_api(self):
        captured = {}
        async def fake_post(url, **kwargs):
            captured["url"] = url
            captured["headers"] = kwargs.get("headers", {})
            return MagicMock(json=MagicMock(return_value=GROQ_RESPONSE), raise_for_status=MagicMock())
        with patch("src.bot.llm_backend.httpx.AsyncClient") as cls:
            mc = AsyncMock()
            mc.__aenter__ = AsyncMock(return_value=mc)
            mc.__aexit__ = AsyncMock(return_value=False)
            mc.post = AsyncMock(side_effect=fake_post)
            cls.return_value = mc
            result = await GroqBackend().complete([{"role": "user", "content": "Hola"}])
        assert "groq.com" in captured["url"] or "api.groq" in captured["url"]
        assert captured["headers"].get("Authorization", "").startswith("Bearer ")
        assert result.backend_name == "groq"


class TestOllamaBackend:
    @pytest.mark.asyncio
    async def test_ollama_backend_calls_api(self):
        captured = {}
        async def fake_post(url, **kwargs):
            captured["url"] = url
            captured["json"] = kwargs.get("json", {})
            return MagicMock(json=MagicMock(return_value=OLLAMA_RESPONSE), raise_for_status=MagicMock())
        with patch("src.bot.llm_backend.httpx.AsyncClient") as cls:
            mc = AsyncMock()
            mc.__aenter__ = AsyncMock(return_value=mc)
            mc.__aexit__ = AsyncMock(return_value=False)
            mc.post = AsyncMock(side_effect=fake_post)
            cls.return_value = mc
            result = await OllamaBackend().complete([{"role": "user", "content": "Hola"}])
        assert "/api/chat" in captured["url"]
        assert captured["json"]["stream"] is False
        assert result.backend_name == "ollama"

    @pytest.mark.asyncio
    async def test_ollama_fallback_to_groq(self):
        groq_result = LLMResponse(content="Groq fallback", backend_name="groq", latency_ms=50.0)
        with patch("src.bot.llm_backend.httpx.AsyncClient") as cls:
            mc = AsyncMock()
            mc.__aenter__ = AsyncMock(return_value=mc)
            mc.__aexit__ = AsyncMock(return_value=False)
            mc.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
            cls.return_value = mc
            with patch.object(GroqBackend, "complete", new_callable=AsyncMock) as mock_groq:
                mock_groq.return_value = groq_result
                result = await OllamaBackend().complete([{"role": "user", "content": "test"}])
        mock_groq.assert_awaited_once()
        assert result.backend_name == "groq"


class TestLLMBackendFactory:
    def test_factory_creates_groq(self, monkeypatch):
        monkeypatch.setenv("LLM_BACKEND", "groq")
        assert isinstance(LLMBackendFactory.create(), GroqBackend)

    def test_factory_creates_ollama(self, monkeypatch):
        monkeypatch.setenv("LLM_BACKEND", "ollama")
        assert isinstance(LLMBackendFactory.create(), OllamaBackend)


class TestLLMResponse:
    @pytest.mark.asyncio
    async def test_llm_response_fields(self):
        async def fake_post(url, **kwargs):
            return MagicMock(json=MagicMock(return_value=OLLAMA_RESPONSE), raise_for_status=MagicMock())
        with patch("src.bot.llm_backend.httpx.AsyncClient") as cls:
            mc = AsyncMock()
            mc.__aenter__ = AsyncMock(return_value=mc)
            mc.__aexit__ = AsyncMock(return_value=False)
            mc.post = AsyncMock(side_effect=fake_post)
            cls.return_value = mc
            result = await OllamaBackend().complete([{"role": "user", "content": "ping"}])
        assert result.content == "Hola desde Ollama"
        assert result.backend_name == "ollama"
        assert result.latency_ms > 0
