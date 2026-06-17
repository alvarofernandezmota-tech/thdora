"""Handler de notas de voz: transcribe audio y procesa con NLP."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.llm_factory import get_router
from src.bot.middleware import require_allowed_user

logger = logging.getLogger(__name__)


@require_allowed_user
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa notas de voz: transcribe con Whisper y reusa el flujo NLP."""
    message = update.effective_message
    if not message or not message.voice:
        return

    await message.chat.send_action("typing")

    try:
        voice_file = await message.voice.get_file()
        audio_bytes = await voice_file.download_as_bytearray()
    except Exception as exc:
        logger.error("Error descargando audio de voz: %s", exc)
        await message.reply_text("❌ No pude descargar el audio. Inténtalo de nuevo.")
        return

    try:
        router = get_router()
        transcription = await router.transcribe(bytes(audio_bytes))
    except Exception as exc:
        logger.error("Error transcribiendo audio: %s", exc)
        await message.reply_text("❌ No pude transcribir el audio. Inténtalo de nuevo.")
        return

    if not transcription or not transcription.strip():
        await message.reply_text("🎙️ No entendí el audio. ¿Puedes repetirlo?")
        return

    logger.info("Voz transcrita para user %s: %s", update.effective_user.id, transcription[:80])

    # Inyectar transcripción como texto y reusar flujo NLP
    update.effective_message = message
    context.user_data["_voice_transcription"] = transcription

    # Importar aquí para evitar circular imports
    from src.bot.handlers.nlp import nlp_handler  # noqa: PLC0415

    # Simular mensaje de texto con la transcripción
    original_text = message.text
    message.text = transcription
    try:
        await nlp_handler(update, context)
    finally:
        message.text = original_text
        context.user_data.pop("_voice_transcription", None)
