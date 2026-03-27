# src/bot/main.py
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from src.bot.handlers import (
    cmd_start, cmd_hoy, cmd_citas, cmd_habito, cmd_resumen
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("hoy", cmd_hoy))
    app.add_handler(CommandHandler("citas", cmd_citas))
    app.add_handler(CommandHandler("habito", cmd_habito))
    app.add_handler(CommandHandler("resumen", cmd_resumen))

    print("🤖 THDORA bot arrancando...")
    app.run_polling()


if __name__ == "__main__":
    main()