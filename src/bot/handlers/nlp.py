import logging
import time
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut

from src.bot.groq_router import GroqRouter
from src.bot.api_client import ApiClient

logger = logging.getLogger(__name__)


class NLPHandler:
    def __init__(self):
        self.router = GroqRouter()
        self.api_client = ApiClient()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        message_text = update.message.text
        chat_id = update.effective_chat.id
        user_id = user.id

        # TAREA 1.1: Anti-timeout — typing inmediato antes de cualquier proceso
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        start_time = time.time()
        logger.info(f"NLP request - user:{user_id} msg:'{message_text[:100]}'")

        try:
            # TAREA 1.3: Contexto dinamico
            today = datetime.now().date().isoformat()
            citas_hoy = self.api_client.get_appointments(user_id, today)
            habitos_activos = self.api_client.get_active_habits(user_id)

            # Memoria corta: ultimos 5 mensajes de la sesion
            history = context.user_data.get('conversation_history', [])[-5:]

            response = await self.router.process_message(
                message=message_text,
                user_id=user_id,
                citas_hoy=citas_hoy,
                habitos=habitos_activos,
                history=history
            )

            # Retry logic con exponential backoff
            for attempt in range(3):
                try:
                    await update.message.reply_text(response)
                    break
                except TimedOut:
                    if attempt == 2:
                        logger.error(f"Final timeout after 3 attempts for user {user_id}")
                        await update.message.reply_text("Toki está pensando... dame un segundo más.")
                    else:
                        await asyncio.sleep(0.5 * (2 ** attempt))
                        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

            # Guardar en historial corto de sesión
            context.user_data.setdefault('conversation_history', []).append(
                {"role": "user", "content": message_text}
            )
            context.user_data['conversation_history'].append(
                {"role": "assistant", "content": response}
            )

            elapsed = time.time() - start_time
            logger.info(f"NLP ok - user:{user_id} time:{elapsed:.2f}s")

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"NLP error user:{user_id} time:{elapsed:.2f}s - {str(e)}",
                exc_info=True
            )
            await update.message.reply_text(
                "Lo siento, tuve un problema interno. Inténtalo de nuevo."
            )
