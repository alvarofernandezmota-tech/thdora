"""Tareas programadas de memoria: resúmenes diarios + limpieza semanal."""
from __future__ import annotations
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


async def daily_memory_summary_job() -> None:
    """Genera resúmenes nocturnos para todos los usuarios activos."""
    logger.info("🔄 Iniciando resúmenes automáticos de memoria...")
    try:
        from src.bot.agents.summary import generate_conversation_summary, update_long_term_memory, get_user_recent_messages
        from src.db.models import UserConfig
        from src.db.session import get_db
        with get_db() as db:
            users = db.query(UserConfig).all()
        for user in users:
            try:
                messages = await get_user_recent_messages(user.user_id)
                if messages:
                    summary = await generate_conversation_summary(messages, getattr(user, "nombre", "Usuario"))
                    await update_long_term_memory(user.user_id, summary)
                    logger.info("✅ Resumen generado para user_id=%s", user.user_id)
            except Exception as exc:
                logger.warning("Error resumiendo user_id=%s: %s", user.user_id, exc)
    except Exception as exc:
        logger.error("daily_memory_summary_job error: %s", exc)


async def memory_cleanup_job() -> None:
    """Limpieza semanal de memoria (checkpoints antiguos + long_term_memory largo)."""
    logger.info("🧹 Iniciando limpieza automática de memoria...")
    try:
        from src.bot.agents.memory import thdora_memory
        thdora_memory.cleanup_old_memory(days_to_keep=90)
        logger.info("✅ Limpieza de memoria finalizada")
    except Exception as exc:
        logger.error("memory_cleanup_job error: %s", exc)


def setup_memory_scheduler(scheduler: AsyncIOScheduler) -> None:
    """Registra todas las tareas de memoria en el scheduler APScheduler."""
    scheduler.add_job(
        daily_memory_summary_job,
        trigger="cron", hour=23, minute=0,
        id="daily_memory_summary", replace_existing=True,
    )
    scheduler.add_job(
        memory_cleanup_job,
        trigger="cron", day_of_week="mon", hour=2, minute=0,
        id="weekly_memory_cleanup", replace_existing=True,
    )
    logger.info("⏰ Tareas de memoria registradas en scheduler")
