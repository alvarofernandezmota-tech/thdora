"""
Entrypoint del bot Telegram de THDORA — v0.21.0
"""
import asyncio
import logging
import os
import sys

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

from src.bot.api_client import ThdoraApiClient
from src.bot.http_client import close_client
from src.bot.scheduler import get_scheduler
from src.config import settings
from src.bot.handlers import (
    build_nueva_handler,
    build_habito_handler,
    build_edit_apt_handler,
    build_edit_hab_handler,
    build_config_handler,
    cb_citas_nav, cb_habitos_nav, cb_semana_nav, cb_menu_home,
    cb_apt_delete, cb_apt_delete_confirm, cb_cita_detail,
    cb_hab_delete, cb_hab_delete_confirm, cb_hab_add, cb_hab_add_value,
    cb_cancel_action,
    cmd_start, cmd_citas, cmd_habitos, cmd_semana, cmd_resumen, cmd_cancelar,
    error_handler,
)
from src.bot.handlers.nlp import nlp_handler
from src.bot.handlers.nlp_disambig import cb_nlp_disambig
from src.bot.handlers.onboarding import get_onboarding_handler
from src.bot.handlers.stats import stats_handler
from src.bot.handlers.diario import diario_handler
from src.bot.handlers.voice import voice_handler
from src.bot.handlers.weather import weather_handler

os.makedirs("data", exist_ok=True)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
for noisy in ("httpx", "telegram.ext", "apscheduler"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

_PERSISTENCE_PATH = os.path.join("data", "bot_persistence.pkl")


async def _check_api() -> None:
    api = ThdoraApiClient()
    ok = await api.health()
    status = "✅" if ok else "⚠️ "
    logger.info("%s API THDORA en %s", status, api.base_url)


async def _post_init(application) -> None:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    logger.info("⏰ Scheduler APScheduler iniciado")

    try:
        from src.agents import build_thdora_graph
        from src.agents.scheduler_tasks import setup_memory_scheduler
        build_thdora_graph()  # pre-compila y cachea
        setup_memory_scheduler(scheduler)
        logger.info("🧠 LangGraph ThdoraAgent + memoria persistente + scheduler listos")
    except ImportError as exc:
        logger.warning("⚠️ langgraph no instalado — usando GroqRouter fallback: %s", exc)


async def _post_shutdown(application) -> None:
    await close_client()
    logger.info("🔌 HTTP client cerrado")


def build_app(token: str):
    persistence = PicklePersistence(filepath=_PERSISTENCE_PATH, update_interval=60)
    app = (
        ApplicationBuilder()
        .token(token)
        .persistence(persistence)
        .post_init(_post_init)
        .post_shutdown(_post_shutdown)
        .build()
    )

    app.add_handler(get_onboarding_handler())
    app.add_handler(build_nueva_handler())
    app.add_handler(build_habito_handler())
    app.add_handler(build_edit_apt_handler())
    app.add_handler(build_edit_hab_handler())
    app.add_handler(build_config_handler())

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
    app.add_handler(CallbackQueryHandler(cb_nlp_disambig,       pattern=r"^nlp_disambig|"))

    app.add_handler(voice_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _route_free_text))

    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("citas",    cmd_citas))
    app.add_handler(CommandHandler("habitos",  cmd_habitos))
    app.add_handler(CommandHandler("semana",   cmd_semana))
    app.add_handler(CommandHandler("resumen",  cmd_resumen))
    app.add_handler(CommandHandler("cancelar", cmd_cancelar))
    app.add_handler(CommandHandler("diario",   diario_handler))
    app.add_handler(CommandHandler("stats",    stats_handler))
    app.add_handler(CommandHandler("tiempo",   weather_handler))

    app.add_error_handler(error_handler)
    return app


async def _route_free_text(update, context) -> None:
    if context.user_data.get("acum_hab_nombre"):
        await cb_hab_add_value(update, context)
        return
    await nlp_handler(update, context)


def main() -> None:
    asyncio.run(_check_api())
    app = build_app(settings.TELEGRAM_BOT_TOKEN)
    logger.info("🧠 THDORA bot v0.21.0 arrancando (polling)…")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
