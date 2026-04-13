"""
Entrypoint del bot Telegram de THDORA — v4.0

Variables de entorno::
    TELEGRAM_BOT_TOKEN   → token de @BotFather (obligatorio)
    THDORA_API_URL       → URL de la FastAPI (por defecto http://localhost:8000)

Orden de registro de handlers:
    1. ConversationHandlers (mayor prioridad; incluyen sus propios entry_points)
       - build_nueva_handler()     /nueva + quick_nueva_*
       - build_habito_handler()    /habito + quick_habito_*
       - build_edit_apt_handler()  ^ae_
       - build_edit_hab_handler()  ^he_
       - build_config_handler()    /config + ^quick_config$
    2. CallbackQueryHandlers globales (navegación, borrado, detalle)
    3. MessageHandler texto libre (acumulación hab fuera de flujos)
    4. CommandHandlers simples
    5. Error handler

Scheduler (F12):
    - Se arranca en post_init (dentro del event loop de PTB, evita RuntimeError)
    - Los jobs diarios (daily_summary / evening_log) se programan en cmd_start
      y se reprograman cuando el usuario cambia horarios en /config
    - Los jobs one-shot de cita se gestionan en handlers/citas.py

NOTA: quick_config NO se registra como handler global independiente.
      Es entry_point de build_config_handler() para entrar en el
      ConversationHandler directamente desde el botón del menú.
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from src.bot.api_client import ThdoraApiClient
from src.bot.scheduler import get_scheduler
from src.bot.handlers import (
    # Factories
    build_nueva_handler,
    build_habito_handler,
    build_edit_apt_handler,
    build_edit_hab_handler,
    build_config_handler,
    # Navegación
    cb_citas_nav,
    cb_habitos_nav,
    cb_semana_nav,
    # Menú
    cb_menu_home,
    # Citas
    cb_apt_delete,
    cb_apt_delete_confirm,
    cb_cita_detail,
    # Hábitos
    cb_hab_delete,
    cb_hab_delete_confirm,
    cb_hab_add,
    cb_hab_add_value,
    # Genérico
    cb_cancel_action,
    # Comandos
    cmd_start,
    cmd_citas,
    cmd_habitos,
    cmd_semana,
    cmd_resumen,
    cmd_cancelar,
    # Error
    error_handler,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def _check_api() -> None:
    api = ThdoraApiClient()
    ok = await api.health()
    if ok:
        logger.info("✅ API de THDORA disponible en %s", api.base_url)
    else:
        logger.warning("⚠️  API de THDORA no responde en %s — el bot arranca igualmente.", api.base_url)


def _load_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado.")
        sys.exit(1)
    return token


def build_app(token: str):
    app = ApplicationBuilder().token(token).build()

    # ── 1. ConversationHandlers ───────────────────────────────────────────
    # IMPORTANTE: quick_config es entry_point de build_config_handler.
    # NO registrar cb_quick_config como handler global o habrá conflicto.
    app.add_handler(build_nueva_handler())     # /nueva + quick_nueva_*
    app.add_handler(build_habito_handler())    # /habito + quick_habito_*
    app.add_handler(build_edit_apt_handler())  # ^ae_
    app.add_handler(build_edit_hab_handler())  # ^he_
    app.add_handler(build_config_handler())    # /config + ^quick_config$

    # ── 2. CallbackQueryHandlers globales ──────────────────────────────
    app.add_handler(CallbackQueryHandler(cb_menu_home,          pattern=r"^menu_home$"))
    app.add_handler(CallbackQueryHandler(cb_citas_nav,          pattern=r"^citas_nav_"))
    app.add_handler(CallbackQueryHandler(cb_habitos_nav,        pattern=r"^habitos_nav_"))
    app.add_handler(CallbackQueryHandler(cb_semana_nav,         pattern=r"^semana_nav_"))
    app.add_handler(CallbackQueryHandler(cb_cita_detail,        pattern=r"^cita_detail_"))
    app.add_handler(CallbackQueryHandler(cb_apt_delete,         pattern=r"^ad_"))
    app.add_handler(CallbackQueryHandler(cb_apt_delete_confirm, pattern=r"^adc_"))
    app.add_handler(CallbackQueryHandler(cb_hab_delete,         pattern=r"^hd_"))
    app.add_handler(CallbackQueryHandler(cb_hab_delete_confirm, pattern=r"^hdc_"))
    app.add_handler(CallbackQueryHandler(cb_hab_add,            pattern=r"^ha_"))
    app.add_handler(CallbackQueryHandler(cb_cancel_action,      pattern=r"^cancel_action$"))

    # ── 3. Texto libre (acumulación fuera de flujos) ──────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _route_free_text))

    # ── 4. Comandos ───────────────────────────────────────────────
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("citas",    cmd_citas))
    app.add_handler(CommandHandler("habitos",  cmd_habitos))
    app.add_handler(CommandHandler("semana",   cmd_semana))
    app.add_handler(CommandHandler("resumen",  cmd_resumen))
    app.add_handler(CommandHandler("cancelar", cmd_cancelar))

    # ── 5. Error handler ────────────────────────────────────────────
    app.add_error_handler(error_handler)

    return app


async def _route_free_text(update, context) -> None:
    """Enruta texto libre fuera de ConversationHandlers.
    Actualmente solo gestiona la acumulación de hábitos (cb_hab_add_value).
    """
    if context.user_data.get("acum_hab_nombre"):
        await cb_hab_add_value(update, context)


def main() -> None:
    token = _load_token()
    asyncio.run(_check_api())
    app = build_app(token)

    async def _post_init(application) -> None:
        """
        Se ejecuta dentro del event loop de PTB — único lugar seguro
        para arrancar AsyncIOScheduler sin RuntimeError.
        No programamos jobs aquí porque no tenemos user_id ni bot listo;
        los jobs diarios se programan en cmd_start por usuario.
        """
        scheduler = get_scheduler()
        if not scheduler.running:
            scheduler.start()
            logger.info("⏰ Scheduler F12 iniciado")

    app.post_init = _post_init

    logger.info("🤖 THDORA bot v4.0 arrancando (polling)…")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
