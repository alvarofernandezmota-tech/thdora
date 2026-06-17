"""Handler NLP: texto libre → get_router() con nlp_history (Sprint 3)."""
from __future__ import annotations
import logging
import traceback
import httpx
from telegram import Update
from telegram.constants import ChatAction
from telegram.error import NetworkError, TimedOut
from telegram.ext import ContextTypes
from src.bot.groq_router import AmbiguityRequest, ToolCallResult
from src.bot.llm_factory import get_router
from src.bot.middleware import require_allowed_user

logger = logging.getLogger(__name__)

_TRIVIALES = {"hola", "ok", "vale", "gracias", "de nada", "👍", "👌", "si", "sí", "no", "buenas", "hey"}


@require_allowed_user
async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa mensajes de texto libre vía get_router() con nlp_history (Sprint 3)."""
    if not update.message or not update.message.text:
        return
    user_text = update.message.text
    user_id = update.effective_user.id if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else 0

    text_lower = user_text.strip().lower()
    if text_lower in _TRIVIALES or len(text_lower) < 3:
        await update.message.reply_text("👋 ¿En qué puedo ayudarte?")
        return

    await update.effective_chat.send_action(ChatAction.TYPING)
    provisional = await update.message.reply_text("⏳ Procesando...")

    router = get_router()
    nlp_history = context.user_data.setdefault("nlp_history", [])

    try:
        result = await router.process(
            user_text=user_text,
            user_id=user_id,
            history=nlp_history,
        )

        nlp_history.append({"role": "user", "content": user_text})
        if isinstance(result, str):
            nlp_history.append({"role": "assistant", "content": result})
        elif hasattr(result, "message_to_user"):
            nlp_history.append({"role": "assistant", "content": result.message_to_user})
        if len(nlp_history) > 20:
            nlp_history[:] = nlp_history[-20:]

        if isinstance(result, ToolCallResult):
            response_text = result.message_to_user
        elif isinstance(result, AmbiguityRequest):
            response_text = result.question_to_user
        else:
            response_text = str(result)

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=provisional.message_id,
            text=response_text,
        )
    except httpx.TimeoutException:
        logger.error("TimeoutException NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="⏳ El servicio tardó demasiado. Inténtalo de nuevo.")
    except httpx.ConnectError:
        logger.error("ConnectError NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="🔌 No se pudo conectar con el servicio de IA.")
    except TimedOut:
        logger.error("TimedOut NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="⏳ Telegram agotó el tiempo de espera. Inténtalo de nuevo.")
    except NetworkError:
        logger.error("NetworkError NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="🔌 Error de red. Comprueba tu conexión.")
    except Exception:
        logger.error("Error inesperado NLP user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(chat_id=chat_id, message_id=provisional.message_id,
            text="❌ Ocurrió un error inesperado.")
