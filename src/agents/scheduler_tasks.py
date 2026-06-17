"""
Tareas programadas de memoria para APScheduler.

Tareas:
- daily_memory_summary_job: Cada noche a las 23:00 — genera resúmenes.
- memory_cleanup_job: Cada lunes a las 02:00 — limpia memoria antigua.

Registro:
    from src.agents.scheduler_tasks import setup_memory_scheduler
    setup_memory_scheduler(scheduler)  # en _post_init del bot
"""
from __future__ import annotations
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


async def daily_memory_summary_job() -> None:
    """Genera resúmenes nocturnos para todos los usuarios activos."""
    logger.info("🔄 Iniciando resúmenes automáticos de memoria...")
    try:
        from src.agents.summarizer import generate_conversation_summary
        from src.agents.memory.long_term import update_long_term_memory
        from src.db.models import UserConfig
        from src.db.session import get_db
        with get_db() as db:
            users = db.query(UserConfig).all()
        for user in users:
            try:
                # TODO Sprint 6: implementar get_user_recent_messages con tabla MessageLog
                messages: list[dict] = []
                if messages:
                    nombre = getattr(user, "nombre", "Usuario") or "Usuario"
                    summary = await generate_conversation_summary(messages, nombre)
                    update_long_term_memory(user.user_id, summary)
                    logger.info("✅ Resumen generado para user_id=%s", user.user_id)
            except Exception as exc:
                logger.warning("Error resumiendo user_id=%s: %s", user.user_id, exc)
    except Exception as exc:
        logger.error("daily_memory_summary_job error: %s", exc)


async def memory_cleanup_job() -> None:
    """Limpieza semanal: recorta long_term_memory + borra checkpoints antiguos."""
    logger.info("🧹 Iniciando limpieza automática de memoria...")
    try:
        from src.agents.memory.manager import memory_manager
        memory_manager.cleanup()
        logger.info("✅ Limpieza de memoria finalizada")
    except Exception as exc:
        logger.error("memory_cleanup_job error: %s", exc)


def setup_memory_scheduler(scheduler: AsyncIOScheduler) -> None:
    """
    Registra las tareas de memoria en APScheduler.

    Args:
        scheduler: Instancia de AsyncIOScheduler ya iniciada.
    """
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
    logger.info("⏰ Tareas de memoria registradas (resumen 23h, limpieza lunes 2h)")
