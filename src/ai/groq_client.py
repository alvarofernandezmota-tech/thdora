# src/ai/groq_client.py
"""
Groq Client for THDORA — v3 with dual model and rate limit handling.

Features:
- Dual model: FAST_MODEL (llama-3.1-8b-instant, 14,400 RPD) for simple intents
- SMART_MODEL (llama-3.3-70b-versatile, 1,000 RPD) for complex NLP
- LRU cache with 5min TTL for identical queries
- Automatic fallback from SMART to FAST on 429
- Rate limit monitoring with warning at < 100 remaining
- Exponential backoff retry (3 attempts, 1-10s)
- 90s timeout
- Dynamic system prompt with current date/time
- Tool calling support with functions.py
- Token usage logging
"""

import logging
import os
import re
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import httpx
from cachetools import TTLCache
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from src.ai.functions import GROQ_FUNCTIONS

logger = logging.getLogger(__name__)

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
FAST_MODEL = "llama-3.1-8b-instant"
SMART_MODEL = "llama-3.3-70b-versatile"
_DEFAULT_MODEL = os.getenv("GROQ_MODEL", FAST_MODEL)
_TIMEOUT = httpx.Timeout(connect=10.0, read=90.0, write=10.0, pool=5.0)

_MSG_TIMEOUT = "Lo siento, tardo un poco más de lo normal. Inténtalo en unos segundos 🙏"
_CACHE: TTLCache = TTLCache(maxsize=256, ttl=300)


class GroqError(Exception):
    """Error in Groq API call."""
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


class GroqClient:
    """
    Async HTTP client for Groq API (OpenAI-compatible).

    Features:
    - Dual model support with automatic fallback
    - LRU cache for identical queries
    - Rate limit monitoring
    - Exponential backoff retry
    - Tool calling support
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_name: str = "Usuario",
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            raise GroqError("GROQ_API_KEY not configured. Add it to .env")
        self.model = model or _DEFAULT_MODEL
        self.user_name = user_name
        self._system_override: Optional[str] = system_prompt
        self._tokens_used: int = 0

    def _get_system(self) -> str:
        return self._system_override or self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        now = datetime.now()
        fecha = now.strftime("%A %d de %B de %Y, %H:%M")
        return f"""Eres THDORA, el asistente personal de {self.user_name}, especializado en gestión de agenda y hábitos diarios.

📅 Hoy es {fecha}.

ROL Y CAPACIDADES:
- Ayudas a gestionar citas, eventos y hábitos personales.
- Tienes acceso a herramientas para consultar, crear y gestionar citas y hábitos.
- Cuando el usuario quiera actuar sobre sus datos, usa las herramientas disponibles.

LÍMITES CLAROS:
- No inventes datos: si no tienes información, dilo con honestidad.
- No accedas a internet ni a información externa.
- No respondas sobre temas ajenos a agenda, hábitos y bienestar personal.
- Si el usuario pregunta algo fuera de tu ámbito, redirígelo amablemente.

FORMATO DE RESPUESTA:
- Conciso: máximo 3 párrafos cortos por respuesta.
- Usa emojis con moderación (1-2 por respuesta).
- Responde siempre en el mismo idioma que el usuario.
- Sé directo: no repitas lo que el usuario ya sabe."""

    def _check_rate_limit(self, response_headers: Dict[str, str]) -> None:
        remaining = int(response_headers.get("x-ratelimit-remaining-requests", 999))
        if remaining < 100:
            logger.warning(f"⚠️ Groq RPD low: {remaining} requests remaining")

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _call_api(self, payload: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Raw API call with retry. Raises GroqError on HTTP error."""
        cache_key = f"{model}:{hash(str(payload))}"
        if cache_key in _CACHE:
            logger.debug("Cache hit for %s", cache_key)
            return {"choices": [{"message": {"content": _CACHE[cache_key]}}]}

        payload["model"] = model
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                _GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            self._check_rate_limit(dict(r.headers))
            if r.is_error:
                detail = ""
                try:
                    detail = r.json().get("error", {}).get("message", r.text[:200])
                except Exception:
                    detail = r.text[:200]
                raise GroqError(f"HTTP {r.status_code}: {detail}", status_code=r.status_code)

            data = r.json()
            response_text = data["choices"][0]["message"]["content"] or ""
            response_text = response_text.strip()
            _CACHE[cache_key] = response_text
            tokens = data.get("usage", {}).get("total_tokens", 0)
            self._tokens_used += tokens
            logger.info(f"Groq [{model}] — {tokens} tokens used (total: {self._tokens_used})")
            return data

    async def call_with_fallback(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call Groq with automatic fallback from SMART to FAST model on 429.

        Args:
            messages: List of {role, content} dicts
            tools: Optional tool schemas for function calling
            user_id: Optional user ID for logging
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Full response dict from Groq API
        """
        system = self._get_system()
        payload: Dict[str, Any] = {
            "messages": [{"role": "system", "content": system}] + messages,
            "temperature": kwargs.get("temperature", 0.4),
            "max_tokens": kwargs.get("max_tokens", 512),
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            return await self._call_api(payload, SMART_MODEL)
        except GroqError as e:
            if e.status_code == 429:
                logger.warning("SMART_MODEL rate limited, falling back to FAST_MODEL")
                return await self._call_api(payload, FAST_MODEL)
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
        max_tokens: int = 512,
        context_block: str = "",
        use_tools: bool = False,
    ) -> str:
        """
        Send messages to Groq and return response text.

        Args:
            messages: List of {role, content}. System prompt added automatically.
            temperature: Creativity (0 deterministic, 1 creative).
            max_tokens: Max tokens in response.
            context_block: Dynamic context to inject into system prompt.
            use_tools: Whether to enable tool calling.

        Returns:
            Response text. On definitive timeout returns friendly message.
        """
        system = self._get_system()
        if context_block:
            system = f"{system}\n\n{context_block}"
            self._system_override = system

        tools = GROQ_FUNCTIONS if use_tools else None
        try:
            response = await self.call_with_fallback(
                messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response["choices"][0]["message"]["content"].strip()
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            logger.error("Definitive timeout with Groq after 3 attempts: %s", exc)
            return _MSG_TIMEOUT
        except GroqError:
            raise

    async def ask(self, user_message: str, **kwargs: Any) -> str:
        """Shortcut: send user message and return response text."""
        return await self.chat([{"role": "user", "content": user_message}], **kwargs)

    def get_tokens_used(self) -> int:
        """Return total tokens used in this session."""
        return self._tokens_used

    def reset_tokens(self) -> None:
        """Reset token counter."""
        self._tokens_used = 0


_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """Return (or create) the global GroqClient instance."""
    global _client
    if _client is None:
        _client = GroqClient()
    return _client


async def ask(message: str, **kwargs: Any) -> str:
    """Global shortcut: ask LLM and return response text."""
    return await get_groq_client().ask(message, **kwargs)
