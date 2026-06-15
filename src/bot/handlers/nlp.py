import logging
import time
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut

from src.bot.groq_router import GroqRouter
from src.bot.api_client import ApiClient
from src.agents.mood_detector import MoodDetector

logger = logging.getLogger(__name__)


class NLPHandler:
    def __init__(self):
        self.router = GroqRouter()
        self.api_client = ApiClient()
        self.mood_detector = MoodDetector(groq_api_key=__import__('os').environ.get('GROQ_API_KEY', ''))

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        message_text = update.message.text
        chat_id = update.effective_chat.id
        user_id = user.id

        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        start_time = time.time()

        try:
            today = datetime.now().date().isoformat()
            citas_hoy, habitos_activos, history = await asyncio.gather(
                self.api_client.get_appointments(user_id, today),
                self.api_client.get_active_habits(user_id),
                self.api_client.get_history(user_id, limit=5),
            )

            # Mood detection cada 5 mensajes
            msg_count = context.user_data.get("msg_count", 0) + 1
            context.user_data["msg_count"] = msg_count
            if msg_count % 5 == 0:
                recent_texts = [m["content"] for m in history if m["role"] == "user"]
                recent_texts.append(message_text)
                asyncio.create_task(
                    self.mood_detector.analyze(recent_texts, user_id)
                )

            mood_context = ""
            if await self.mood_detector.should_mention(user_id):
                mood_context = (
                    "\n[CONTEXTO INTERNO: el usuario lleva varios dias con estado "
                    "emocional bajo. Muestra empatia de forma natural, sin ser invasivo.]"
                )

            response = await self.router.process_message(
                message=message_text,
                user_id=user_id,
                citas_hoy=citas_hoy,
                habitos=habitos_activos,
                history=history,
                extra_context=mood_context,
            )

            for attempt in range(3):
                try:
                    await update.message.reply_text(response)
                    break
                except TimedOut:
                    if attempt == 2:
                        await update.message.reply_text(
                            "THDORA esta pensando... dame un segundo mas."
                        )
                    else:
                        await asyncio.sleep(0.5 * (2 ** attempt))
                        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

            await asyncio.gather(
                self.api_client.save_message(user_id, "user", message_text),
                self.api_client.save_message(user_id, "assistant", response),
            )

            elapsed = time.time() - start_time
            logger.info("NLP ok - user:%s time:%.2fs", user_id, elapsed)

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error("NLP error user:%s time:%.2fs - %s", user_id, elapsed, str(e), exc_info=True)
            await update.message.reply_text(
                "Lo siento, tuve un problema interno. Intentalo de nuevo."
            )
