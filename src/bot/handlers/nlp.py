"""
Handler NLP — Sprint 5.
Arquitectura 3 capas:
  Nivel 0: Regex rápido (≤200ms, sin LLM)
  Nivel 1: Filtro triviales
  Nivel 2: Fallback llm_factory (Ollama -> Groq)
"""
from __future__ import annotations

import logging
import re
import traceback

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from src.bot.llm_factory import get_router
from src.bot.middleware import require_allowed_user

logger = logging.getLogger(__name__)

# Nivel 0 — regex (orden importa: más específicos primero)
_REGEX_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r'^(hola|buenos?\s*(d[ií]as?|noches?|tardes?)|hey|buenas?)[\.!]?$', re.I),
     "👋 ¡Hola! ¿En qué te ayudo hoy?"),
    (re.compile(r'^(adiós|adios|chau|hasta luego|nos vemos|bye|hasta pronto)[\.!]?$', re.I),
     "👋 ¡Hasta pronto! Cuídate."),
    (re.compile(r'(crear|programar|nueva|añadir|pon|agrega)\b.{0,30}\b(cita|reunión|reunion|dentista|médico|medico|recordatorio)', re.I),
     "📅 Vamos a crear una cita. Usa /nueva para empezar."),
    (re.compile(r'(ver|muestra|lista|mis|cuáles?|cuales?)\b.{0,20}\b(citas?|agenda)', re.I),
     "📅 Usa /citas para ver tu agenda."),
    (re.compile(r'(crear|registrar|añadir|nuevo)\b.{0,20}\b(hábito|habito)', re.I),
     "🏃 Usa /habito para crear un nuevo hábito."),
    (re.compile(r'(ver|muestra|mis|progreso)\b.{0,20}\b(hábitos?|habitos?)', re.I),
     "📊 Usa /habitos para ver tu progreso."),
    (re.compile(r'(qué|que)\s+(tiempo|clima)\s+(hay|hace|está|esta)', re.I),
     "🌤️ Usa /tiempo [ciudad] para ver el clima."),
    (re.compile(r'^(gracias|de nada|perfecto|genial|ok|vale|bien|super|sí|si|no)[\s\.!]?$', re.I),
     "😊 ¿Hay algo más en lo que pueda ayudarte?"),
]

_TRIVIALES: frozenset[str] = frozenset({"👍", "👌", "❤️", "🙏", "😀", "😄"})


def _try_regex(text: str) -> str | None:
    for pattern, response in _REGEX_RULES:
        if pattern.search(text):
            return response
    return None


@require_allowed_user
async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    user_id = update.effective_user.id if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else 0

    # Nivel 0a — emojis triviales
    if user_text in _TRIVIALES or len(user_text) < 2:
        await update.message.reply_text("😊 ¿En qué puedo ayudarte?")
        return

    # Nivel 0b — regex
    regex_reply = _try_regex(user_text)
    if regex_reply:
        logger.info("🔍 Regex match user_id=%s | '%s'", user_id, user_text[:50])
        await update.message.reply_text(regex_reply)
        return

    # Nivel 2 — LLM (Ollama -> Groq via llm_factory)
    await update.effective_chat.send_action(ChatAction.TYPING)
    provisional = await update.message.reply_text("⏳ Procesando...")

    router = get_router()
    nlp_history: list[dict] = context.user_data.setdefault("nlp_history", [])

    try:
        result = await router.process(
            user_text=user_text,
            user_id=user_id,
            history=nlp_history,
        )
        reply_text = result.get("text", "") if isinstance(result, dict) else str(result)

        # Historial: máx 20 turnos (40 entradas)
        nlp_history.append({"role": "user", "content": user_text})
        nlp_history.append({"role": "assistant", "content": reply_text})
        if len(nlp_history) > 40:
            nlp_history[:] = nlp_history[-40:]

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=provisional.message_id,
            text=reply_text or "❓ Sin respuesta del modelo.",
        )

    except Exception:
        logger.error("❌ Error NLP: %s", traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=provisional.message_id,
            text="❌ Error inesperado. Inténtalo de nuevo.",
        )
