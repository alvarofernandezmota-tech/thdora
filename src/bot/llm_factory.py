"""LLM Factory — Arquitectura de 3 niveles (Sprint 5/6).

Nivel 0: Regex        → nlp.py (NO toca este archivo)
Nivel 1: Ollama local → qwen2.5:3b-instruct, timeout 500ms, temp 0.0
Nivel 2: Groq cloud   → llama-3.3-70b-versatile, historial completo
"""
from __future__ import annotations

import json
import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

_INTENT_RESPONSES: dict[str, str] = {
    "saludo": "¡Hola! ¿En qué te ayudo hoy?",
    "despedida": "¡Hasta luego! Cuídate.",
    "ver_citas": "Mostrando tus citas...",
    "ver_habitos": "Mostrando tus hábitos...",
    "ver_resumen": "Generando resumen...",
    "tiempo": "Consultando el clima...",
}

_SYSTEM_PROMPT_L1 = (
    "Eres un clasificador de intenciones. Responde ÚNICAMENTE con JSON válido, sin texto extra.\n"
    'Formato: {"intent": "<intención>", "confidence": <0.0-1.0>}\n'
    "Intenciones posibles: saludo, despedida, crear_cita, ver_citas, crear_habito, "
    "ver_habitos, ver_resumen, ver_stats, tiempo, diario, otro"
)


class Level1OllamaClassifier:
    """Nivel 1: Clasificador rápido local con Ollama (qwen2.5:3b)."""

    def __init__(self) -> None:
        self.host = settings.OLLAMA_HOST.rstrip("/")
        self.model = settings.OLLAMA_MODEL_LEVEL1
        self._timeout = httpx.Timeout(0.5)  # 500 ms

    async def classify(self, text: str) -> dict | None:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT_L1},
                {"role": "user", "content": text},
            ],
            "temperature": 0.0,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self.host}/api/chat", json=payload)
                resp.raise_for_status()
                content = resp.json()["message"]["content"].strip()
                parsed = json.loads(content)
                if "intent" in parsed and "confidence" in parsed:
                    return {
                        "intent": str(parsed["intent"]),
                        "confidence": float(parsed["confidence"]),
                    }
        except (httpx.TimeoutException, json.JSONDecodeError, KeyError, Exception) as exc:
            logger.debug("Nivel 1 falló (%s): %s", type(exc).__name__, exc)
        return None


class LLMFactory:
    """Gestor de enrutamiento multinivel. Interfaz pública: process()."""

    def __init__(self) -> None:
        self.classifier = Level1OllamaClassifier()

    async def process(
        self, user_text: str, user_id: int, history: list[dict]
    ) -> dict:
        """Procesa el mensaje aplicando los niveles 1 y 2.

        Nivel 0 (regex) ya fue ejecutado por nlp.py antes de llegar aquí.
        Retorna: {"text": str, "intent": str, "level_used": int}
        """
        # ── Nivel 1 ──────────────────────────────────────────────────────────
        classification = await self.classifier.classify(user_text)

        if classification and classification.get("confidence", 0.0) >= 0.75:
            intent = classification["intent"]
            logger.info(
                "[user=%s] Nivel 1 → intent=%s conf=%.2f",
                user_id, intent, classification["confidence"],
            )
            return {
                "text": _INTENT_RESPONSES.get(intent, "Entendido."),
                "intent": intent,
                "level_used": 1,
            }

        # ── Nivel 2: Groq ─────────────────────────────────────────────────────
        logger.info("[user=%s] Escalando a Nivel 2 (Groq)", user_id)
        from src.bot.groq_router import GroqRouter  # import lazy — no rompe imports existentes

        groq = GroqRouter()
        result = await groq.process(user_text, user_id=user_id, history=history)
        return {
            "text": result.get("text", "No pude procesar el mensaje."),
            "intent": result.get("intent", "otro"),
            "level_used": 2,
        }


def get_router() -> LLMFactory:
    """Devuelve instancia del router. Interfaz compatible con nlp.py."""
    return LLMFactory()
