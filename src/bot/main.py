# src/bot/main.py
import logging
import os
from typing import Any

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.bot.handlers.commands import (
    cmd_start, cmd_help, cmd_citas, cmd_nueva, cmd_borrar,
    cmd_habito, cmd_diario, cmd_semana
)
from src.bot.handlers.nlp import nlp_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("THDORA_BOT_TOKEN")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("citas", cmd_citas))
    application.add_handler(CommandHandler("nueva", cmd_nueva))
    application.add_handler(CommandHandler("borrar", cmd_borrar))
    application.add_handler(CommandHandler("habito", cmd_habito))
    application.add_handler(CommandHandler("diario", cmd_diario))
    application.add_handler(CommandHandler("semana", cmd_semana))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nlp_handler))

    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
