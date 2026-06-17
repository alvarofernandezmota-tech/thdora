"""OllamaRouter: NLP vía Ollama API local. Misma interfaz que GroqRouter."""
from __future__ import annotations

import json
import logging
from functools import lru_cache

import httpx

from src.bot.http_client import get_client
from src.bot.groq_router import AmbiguityRequest, ToolCallResult, TOOLS
from src.config import settings

logger = logging.getLogger(__name__)

_OLLAMA_TIMEOUT = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0)


@lru_cache(maxsize=32)
def _build_system_prompt(nombre_usuario: str | None = None) -> str:
    nombre = nombre_usuario or "Usuario"
    return f"""Eres Toki, asistente personal de {nombre}. Gestionas citas y hábitos.

## ROL
Ayudas a {nombre} con agenda y hábitos. Interpretas lenguaje natural en español.

## LÍMITES
- SOLO agenda, citas, recordatorios y hábitos.
- Sin consejos médicos, legales, financieros ni contenido creativo.

## RESPUESTA
Responde SIEMPRE con JSON válido:
{{"intent":"<crear_cita|borrar_cita|consultar_citas|consultar_semana|registrar_habito|fuera_de_scope|aclaracion>",
"accion":"<accion o null>","entidades":{{}},"respuesta_usuario":"<mensaje en español>"}}

## REGLAS
- Fechas relativas las resuelves con la hora del contexto.
- Si falta fecha/hora obligatoria: intent "aclaracion", pregunta solo lo que falta.
- Responde en español, tono amigable y conciso. No inventes datos.
"""


class OllamaRouter:
    """Router NLP que usa Ollama local. Misma interfaz que GroqRouter."""

    def __init__(self) -> None:
        self._host: str = getattr(settings, "OLLAMA_HOST", "http://localhost:11434")
        self._model: str = getattr(settings, "OLLAMA_MODEL", "llama3")

    async def process(
        self,
        user_text: str,
        user_id: int = 0,
        nombre_usuario: str | None = None,
        context_str: str = "",
        timeout: httpx.Timeout | None = None,
        history: list[dict] | None = None,
    ) -> str | ToolCallResult | AmbiguityRequest:
        """Procesa un mensaje vía Ollama y devuelve respuesta o acción."""
        _timeout = timeout or _OLLAMA_TIMEOUT
        system_prompt = _build_system_prompt(nombre_usuario)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        if context_str:
            messages.append({"role": "system", "content": f"CONTEXTO:\n{context_str}"})
        if history:
            messages.extend(history[-10:])
        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 256},
        }

        try:
            resp = await get_client().post(
                f"{self._host}/api/chat",
                json=payload,
                timeout=_timeout,
            )
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
        except Exception as exc:
            logger.error("OllamaRouter error: %s", exc)
            return "❌ Error conectando con Ollama. Comprueba que está activo en Madre."

        try:
            parsed = json.loads(content)
            return parsed.get("respuesta_usuario", content)
        except (json.JSONDecodeError, AttributeError):
            return content

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcripción de voz — Ollama no soporta Whisper, delega a Groq."""
        logger.warning("OllamaRouter.transcribe() → delegando a GroqRouter")
        from src.bot.groq_router import GroqRouter  # noqa: PLC0415

        return await GroqRouter().transcribe(audio_bytes)
