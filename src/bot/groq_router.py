"""Router Nivel 2 (Groq) — Sprint 5/6.

Este módulo faltaba: llm_factory.py lo importaba de forma lazy
(`from src.bot.groq_router import GroqRouter`) pero el archivo nunca
se creó. Envuelve src.ai.intent_parser.parse_intent (ya existente y
probado) con el contrato {"text", "intent"} que LLMFactory.process()
espera del Nivel 2.

Uso:
    from src.bot.groq_router import GroqRouter
    router = GroqRouter()
    result = await router.process(user_text, user_id=123, history=[])
    # {"text": "...", "intent": "..."}
"""
from __future__ import annotations

import logging

from src.ai.intent_parser import parse_intent

logger = logging.getLogger(__name__)

_FALLBACK_REPLIES: dict[str, str] = {
    "ver_citas": "📅 Usa /citas para ver tu agenda.",
    "crear_cita": "📅 Vamos a crear una cita. Usa /nueva para empezar.",
    "ver_habitos": "📊 Usa /habitos para ver tu progreso.",
    "registrar_habito": "🏃 Usa /habito para crear un nuevo hábito.",
    "ver_resumen": "📋 Usa /resumen para ver tu resumen.",
    "desconocido": "🤔 No estoy seguro de haber entendido. ¿Puedes reformularlo?",
}


class GroqRouter:
    """Nivel 2 del pipeline NLP: delega en el parser de intenciones de Groq."""

    async def process(
        self, user_text: str, user_id: int, history: list[dict]
    ) -> dict:
        """Procesa el texto del usuario vía Groq y devuelve {"text", "intent"}.

        Args:
            user_text: Mensaje del usuario.
            user_id:   ID de Telegram (para logging).
            history:   Historial de la conversación (mantenido en firma
                       por compatibilidad con LLMFactory.process()).

        Returns:
            Dict con "text" (respuesta a mostrar) e "intent" (intención detectada).
            Nunca lanza excepción — parse_intent ya captura errores internamente.
        """
        data = await parse_intent(user_text)
        intent = data.get("intent", "desconocido")

        if intent == "chat" and data.get("reply"):
            text = data["reply"]
        else:
            text = _FALLBACK_REPLIES.get(intent, "Entendido.")

        logger.info("[user=%s] GroqRouter Nivel 2 → intent=%s", user_id, intent)

        return {"text": text, "intent": intent}
