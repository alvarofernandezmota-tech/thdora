"""LLM Factory: devuelve el router NLP según LLM_BACKEND en la configuración.

Sprint 4 — fallback automático: si OllamaRouter.process() tarda más de 3s
o lanza excepción, reintenta con GroqRouter. Log WARNING "fallback groq: <motivo>".
"""
from __future__ import annotations

import asyncio
import logging

from src.config import settings

logger = logging.getLogger(__name__)

_OLLAMA_TIMEOUT_S = 3.0


class _RouterWithFallback:
    """Wrapper que intenta OllamaRouter y cae a GroqRouter si falla o tarda > 3s."""

    def __init__(self, primary, fallback):
        self._primary = primary
        self._fallback = fallback

    async def process(self, *args, **kwargs):
        try:
            result = await asyncio.wait_for(
                self._primary.process(*args, **kwargs),
                timeout=_OLLAMA_TIMEOUT_S,
            )
            return result
        except asyncio.TimeoutError:
            motivo = f"timeout >{_OLLAMA_TIMEOUT_S}s"
            logger.warning("fallback groq: %s", motivo)
            return await self._fallback.process(*args, **kwargs)
        except Exception as exc:
            motivo = str(exc) or type(exc).__name__
            logger.warning("fallback groq: %s", motivo)
            return await self._fallback.process(*args, **kwargs)

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcripción siempre via Groq (Ollama no soporta Whisper)."""
        return await self._fallback.transcribe(audio_bytes)


def get_router():
    """Devuelve el router NLP según settings.LLM_BACKEND.

    LLM_BACKEND="groq"   → GroqRouter (default, producción)
    LLM_BACKEND="ollama" → _RouterWithFallback(OllamaRouter, GroqRouter)
    """
    backend = getattr(settings, "LLM_BACKEND", "groq").lower()

    if backend == "ollama":
        from src.bot.ollama_router import OllamaRouter
        from src.bot.groq_router import GroqRouter
        logger.debug("LLM backend: OllamaRouter con fallback a GroqRouter (timeout=%ss)", _OLLAMA_TIMEOUT_S)
        return _RouterWithFallback(OllamaRouter(), GroqRouter())

    from src.bot.groq_router import GroqRouter
    logger.debug("LLM backend: GroqRouter")
    return GroqRouter()
