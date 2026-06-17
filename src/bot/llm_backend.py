"""Patrón Strategy para backends LLM intercambiables: Groq y Ollama."""

from __future__ import annotations

import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[dict] | None = field(default=None)
    model_used: str = ""
    latency_ms: float = 0.0
    backend_name: str = ""
    raw: dict = field(default_factory=dict)


class LLMBackend(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> LLMResponse: ...


class GroqBackend(LLMBackend):
    def __init__(self) -> None:
        self._api_key: str = os.environ["GROQ_API_KEY"]
        self._model: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        self._base_url: str = "https://api.groq.com/openai/v1/chat/completions"

    async def complete(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> LLMResponse:
        _timeout = timeout or httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)
        payload: dict = {"model": self._model, "messages": messages, "max_tokens": 1024, "temperature": 0.1}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        t0 = time.monotonic()
        async with httpx.AsyncClient(timeout=_timeout) as client:
            resp = await client.post(self._base_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        latency = (time.monotonic() - t0) * 1000
        choice = data["choices"][0]["message"]
        return LLMResponse(
            content=choice.get("content") or "",
            tool_calls=choice.get("tool_calls") or None,
            model_used=data.get("model", self._model),
            latency_ms=round(latency, 2),
            backend_name="groq",
            raw=data,
        )


class OllamaBackend(LLMBackend):
    """Backend LLM usando Ollama local con fallback automático a Groq."""

    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    async def complete(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> LLMResponse:
        """Llama a Ollama; si no está disponible, delega a GroqBackend."""
        url = f"{self.OLLAMA_HOST}/api/chat"
        payload: dict[str, Any] = {"model": self.OLLAMA_MODEL, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        t0 = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            logger.warning("Ollama no disponible, usando Groq como fallback: %s", exc)
            return await GroqBackend().complete(messages, tools=tools)
        latency_ms = (time.monotonic() - t0) * 1000
        data = resp.json()
        message = data.get("message", {})
        return LLMResponse(
            content=message.get("content", ""),
            tool_calls=message.get("tool_calls") or None,
            backend_name="ollama",
            latency_ms=latency_ms,
            raw=data,
        )


class LLMBackendFactory:
    _REGISTRY: dict[str, type[LLMBackend]] = {"groq": GroqBackend, "ollama": OllamaBackend}

    @classmethod
    def create(cls, backend: str | None = None) -> LLMBackend:
        name = (backend or os.getenv("LLM_BACKEND", "groq")).lower().strip()
        klass = cls._REGISTRY.get(name)
        if klass is None:
            raise ValueError(f"Backend '{name}' no reconocido. Opciones: {list(cls._REGISTRY)}")
        return klass()
