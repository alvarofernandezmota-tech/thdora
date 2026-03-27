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

Handlers registrados::

    Comandos:   /start  /citas  /habitos  /resumen  /cancelar
    Flujos:     /nueva (5 pasos)  /habito (2 pasos)
    Edición:   editar cita (4 pasos)  editar hábito (1 paso)
    Inline:     borrar/confirmar cita, borrar/confirmar hábito,
                acumular hábito, cancelar acción

Orden de registro (importante para python-telegram-bot):
    1. ConversationHandlers (mayor prioridad, capturan callbacks propios)
    2. CallbackQueryHandlers globales (borrar, confirmar, acumular)
    3. CommandHandlers simples
    4. Error handler
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from src.bot.api_client import ThdoraApiClient
from src.bot.handlers import (
    build_edit_apt_handler,
    build_edit_hab_handler,
    build_habito_handler,
    build_nueva_handler,
    cb_apt_delete,
    cb_apt_delete_confirm,
    cb_cancel_action,
    cb_hab_add,
    cb_hab_add_value,
    cb_hab_delete,
    cb_hab_delete_confirm,
    cmd_cancelar,
    cmd_citas,
    cmd_habitos,
    cmd_resumen,
    cmd_start,
    error_handler,
)
from telegram.ext import MessageHandler, filters

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
    """Comprueba si la API está disponible al arrancar. No bloquea."""
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
    """Lee TELEGRAM_BOT_TOKEN del entorno. Sale con error si no existe."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        logger.error(
            "TELEGRAM_BOT_TOKEN no está configurado. "
            "Añádelo al .env o expórtalo antes de arrancar el bot."
        )
        sys.exit(1)
    return token


def build_app(token: str):
    """
    Construye la aplicación de Telegram con todos los handlers.

    Orden de registro:
        1. ConversationHandlers (capturan sus propios entry_points y callbacks)
        2. CallbackQueryHandlers globales (los que no pertenecen a ningún flujo)
        3. MessageHandler para acumulación de hábitos (texto fuera de flujo)
        4. CommandHandlers simples
        5. Error handler
    """
    app = ApplicationBuilder().token(token).build()

    # ── 1. ConversationHandlers ─────────────────────────────────────
    app.add_handler(build_nueva_handler())
    app.add_handler(build_habito_handler())
    app.add_handler(build_edit_apt_handler())   # activado por ^ae_ inline
    app.add_handler(build_edit_hab_handler())   # activado por ^he_ inline

    # ── 2. CallbackQueryHandlers globales ─────────────────────────────
    # Citas
    app.add_handler(CallbackQueryHandler(cb_apt_delete,         pattern=r"^ad_"))
    app.add_handler(CallbackQueryHandler(cb_apt_delete_confirm, pattern=r"^adc_"))
    # Hábitos
    app.add_handler(CallbackQueryHandler(cb_hab_delete,         pattern=r"^hd_"))
    app.add_handler(CallbackQueryHandler(cb_hab_delete_confirm, pattern=r"^hdc_"))
    app.add_handler(CallbackQueryHandler(cb_hab_add,            pattern=r"^ha_"))
    # Genérico
    app.add_handler(CallbackQueryHandler(cb_cancel_action,      pattern=r"^cancel_action$"))

    # ── 3. MessageHandler para acumulación (texto libre fuera de flujo) ───
    # Solo se activa si hay contexto acum_hab_nombre en user_data
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            _route_free_text,
        )
    )

    # ── 4. CommandHandlers simples ─────────────────────────────────
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("citas",   cmd_citas))
    app.add_handler(CommandHandler("habitos", cmd_habitos))
    app.add_handler(CommandHandler("resumen", cmd_resumen))
    app.add_handler(CommandHandler("cancelar",cmd_cancelar))

    # ── 5. Error handler ─────────────────────────────────────────
    app.add_error_handler(error_handler)

    return app


async def _route_free_text(
    update, context
) -> None:
    """
    Enruta texto libre fuera de flujos de conversación.

    Si hay un hábito pendiente de acumulación en user_data,
    delega en cb_hab_add_value. En caso contrario, ignora.
    """
    if context.user_data.get("acum_hab_nombre"):
        from src.bot.handlers import cb_hab_add_value
        await cb_hab_add_value(update, context)


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
