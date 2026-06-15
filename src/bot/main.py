# src/bot/main.py
"""
THDORA Telegram Bot — Main entry point.

Features:
- Command handlers: /start, /help, /citas, /nueva, /borrar, /habito, /diario, /semana
- NLP handler for natural language processing
- Global error handler to prevent silent crashes
- Robust polling with timeout configuration
"""

import logging
import os
from typing import Any

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from src.bot.handlers.commands import (
    cmd_start,
    cmd_help,
    cmd_citas,
    cmd_nueva,
    cmd_borrar,
    cmd_habito,
    cmd_diario,
    cmd_semana,
)
from src.bot.handlers.nlp import nlp_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("THDORA_BOT_TOKEN")


async def error_handler(update: Any, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global error handler — prevents silent crashes.
    Logs all exceptions and sends user-friendly error message.
    """
    logger.error(f"Exception in Telegram bot: {context.error}", exc_info=context.error)
    if update and hasattr(update, "effective_message") and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Error interno\. Inténtalo de nuevo más tarde\.",
                parse_mode="MarkdownV2"
            )
        except Exception:
            pass


def main() -> None:
    """Start the THDORA Telegram bot."""
    if not TOKEN:
        raise RuntimeError("THDORA_BOT_TOKEN not set in environment")

    application = Application.builder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("citas", cmd_citas))
    application.add_handler(CommandHandler("nueva", cmd_nueva))
    application.add_handler(CommandHandler("borrar", cmd_borrar))
    application.add_handler(CommandHandler("habito", cmd_habito))
    application.add_handler(CommandHandler("diario", cmd_diario))
    application.add_handler(CommandHandler("semana", cmd_semana))

    # NLP handler for free text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nlp_handler))

    # Global error handler
    application.add_error_handler(error_handler)

    logger.info("🤖 THDORA bot starting...")
    application.run_polling(
        allowed_updates=["message", "callback_query"],
        timeout=30,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=30,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
