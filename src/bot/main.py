"""
Entrypoint del bot Telegram de THDORA.

Lee el token de la variable de entorno ``TELEGRAM_BOT_TOKEN``,
registra todos los handlers y arranca el bot en modo polling.

Variables de entorno::

    TELEGRAM_BOT_TOKEN   → token de @BotFather (obligatorio)
    THDORA_API_URL       → URL de la FastAPI (por defecto http://localhost:8000)

Ejecución::

    # Opción 1 — Makefile
    make run-bot

    # Opción 2 — directo
    python -m src.bot.main

Dependencias::

    python-telegram-bot >= 21.0
    httpx >= 0.27.0
    python-dotenv >= 1.0.0
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

from src.bot.api_client import ThdoraApiClient
from src.bot.handlers import (
    build_habito_handler,
    build_nueva_handler,
    cmd_borrar,
    cmd_cancelar,
    cmd_citas,
    cmd_habitos,
    cmd_resumen,
    cmd_start,
    error_handler,
)

# Cargar .env antes de leer variables de entorno
load_dotenv()

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def _check_api() -> None:
    api = ThdoraApiClient()
    ok = await api.health()
    if ok:
        logger.info("✅ API de THDORA disponible en %s", api.base_url)
    else:
        logger.warning(
            "⚠️  API de THDORA no responde en %s — el bot arranca igualmente, "
            "pero los comandos fallarán hasta que la API esté activa.",
            api.base_url,
        )


def _load_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        logger.error(
            "TELEGRAM_BOT_TOKEN no está configurado. "
            "Añádelo al .env o expórtalo antes de arrancar el bot."
        )
        sys.exit(1)
    return token


def build_app(token: str):
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("citas", cmd_citas))
    app.add_handler(CommandHandler("borrar", cmd_borrar))
    app.add_handler(CommandHandler("habitos", cmd_habitos))
    app.add_handler(CommandHandler("resumen", cmd_resumen))
    app.add_handler(CommandHandler("cancelar", cmd_cancelar))

    app.add_handler(build_nueva_handler())
    app.add_handler(build_habito_handler())

    app.add_error_handler(error_handler)

    return app


def main() -> None:
    token = _load_token()
    asyncio.run(_check_api())
    app = build_app(token)
    logger.info("🤖 THDORA bot arrancando (polling)…")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
