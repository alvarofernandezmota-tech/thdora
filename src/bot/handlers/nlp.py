"""Handler NLP: patrón mensaje provisional + edición para evitar TimedOut de Telegram."""

from __future__ import annotations

import logging
import traceback

import httpx
from telegram import Update
from telegram.error import NetworkError, TimedOut
from telegram.ext import ContextTypes

from src.bot.groq_router import GroqRouter

logger = logging.getLogger(__name__)


async def nlp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa mensajes de texto libre via GroqRouter con patrón provisional+edición."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_id = update.effective_user.id if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else 0

    provisional = await update.message.reply_text("⏳ Procesando...")

    groq_router: GroqRouter = context.bot_data.get("groq_router") or GroqRouter()

    try:
        response_text = await groq_router.process(
            user_text=user_text,
            user_id=user_id,
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0),
        )
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=provisional.message_id,
            text=response_text,
        )

    except httpx.TimeoutException:
        logger.error("TimeoutException en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="⌛ El servicio tardó demasiado en responder. Inténtalo de nuevo.",
        )

    except httpx.ConnectError:
        logger.error("ConnectError en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="🔌 No se pudo conectar con el servicio de IA. Verifica la conexión.",
        )

    except TimedOut:
        logger.error("TimedOut de Telegram en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="⌛ Telegram agotó el tiempo de espera. Inténtalo de nuevo.",
        )

    except NetworkError:
        logger.error("NetworkError de Telegram en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="📡 Error de red. Comprueba tu conexión e inténtalo de nuevo.",
        )

    except Exception:
        logger.error("Error inesperado en NLP para user_id=%s: %s", user_id, traceback.format_exc())
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=provisional.message_id,
            text="❌ Ocurrió un error inesperado. El equipo ha sido notificado.",
        )
