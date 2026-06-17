"""Handler NLP: texto libre → GroqRouter con seguridad, TYPING y filtro de triviales."""
from __future__ import annotations

import logging
import traceback

import httpx
from telegram import Update
from telegram.constants import ChatAction
from telegram.error import NetworkError, TimedOut
from telegram.ext import ContextTypes

from src.bot.groq_router import AmbiguityRequest, GroqRouter, ToolCallResult
from src.bot.middleware import require_allowed_user

logger = logging.getLogger(__name__)

# Mensajes triviales que no merecen una llamada a Groq
_TRIVIALES = {"hola", "ok", "vale", "gracias", "de nada", "\ud83d\udc4d", "\ud83d\udc4c", "si", "s\u00ed", "no", "buenas", "hey"}


@require_allowed_user
async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa mensajes de texto libre vía GroqRouter con patrón provisional+edición."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_id = update.effective_user.id if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else 0

    # Pre-filtro: mensajes triviales — respuesta instantánea sin llamar a Groq
    text_lower = user_text.strip().lower()
    if text_lower in _TRIVIALES or len(text_lower) < 3:
        await update.message.reply_text("\ud83d� \u00bfEn qué puedo ayudarte?")
        return

    # Indicador visual de procesamiento
    await update.effective_chat.send_action(ChatAction.TYPING)

    provisional = await update.message.reply_text("\u23f3 Procesando...")

    groq_router: GroqRouter = context.bot_data.get("groq_router") or GroqRouter()

    try:
        result = await groq_router.process(
            user_text=user_text,
            user_id=user_id,
        )

        # Resolver el tipo de respuesta
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
        logger.error("TimeoutException en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="\u231b El servicio tardó demasiado en responder. Inténtalo de nuevo.",
        )

    except httpx.ConnectError:
        logger.error("ConnectError en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="\ud83d� No se pudo conectar con el servicio de IA. Verifica la conexión.",
        )

    except TimedOut:
        logger.error("TimedOut de Telegram en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="\u231b Telegram agotó el tiempo de espera. Inténtalo de nuevo.",
        )

    except NetworkError:
        logger.error("NetworkError de Telegram en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="\ud83d� Error de red. Comprueba tu conexión e inténtalo de nuevo.",
        )

    except Exception:
        logger.error("Error inesperado en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="\u274c Ocurrió un error inesperado. El equipo ha sido notificado.",
        )
