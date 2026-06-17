"""LLM Factory: devuelve el router NLP según LLM_BACKEND en la configuración."""
from __future__ import annotations

import logging

from src.config import settings

logger = logging.getLogger(__name__)


def get_router():
    """Devuelve GroqRouter u OllamaRouter según settings.LLM_BACKEND.

    LLM_BACKEND="groq"   → GroqRouter (default, producción)
    LLM_BACKEND="ollama" → OllamaRouter (local, Madre)
    """
    backend = getattr(settings, "LLM_BACKEND", "groq").lower()

    if backend == "ollama":
        from src.bot.ollama_router import OllamaRouter  # noqa: PLC0415

        logger.debug("LLM backend: OllamaRouter")
        return OllamaRouter()

    from src.bot.groq_router import GroqRouter  # noqa: PLC0415

    logger.debug("LLM backend: GroqRouter")
    return GroqRouter()
