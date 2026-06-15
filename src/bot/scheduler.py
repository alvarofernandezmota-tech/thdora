"""
Scheduler de notificaciones proactivas — F12 adaptado a multi-usuario.

Jobs:
    daily_summary_{user_id}                       → resumen de citas del día (default 08:00)
    evening_log_{user_id}                         → recordatorio hábitos (default 22:00)
    apt_reminder_{user_id}_{apt_id}_{offset_min}  → aviso X min antes de cita (one-shot)

Arquitectura multi-usuario:
    - _subscribed_users: Set[int] con user_ids suscritos
    - subscribe_user / unsubscribe_user gestionan la lista
    - Cada job itera _subscribed_users y envía a cada uno
    - user_id siempre dinámico, nunca hardcoded del .env

Uso desde handlers::

    from src.bot.scheduler import subscribe_user, schedule_apt_reminders, cancel_apt_reminders
    subscribe_user(update.effective_user.id)
    schedule_apt_reminders(bot, user_id, apt_dict, cfg_dict)

Uso desde main.py::

    from src.bot.scheduler import setup_scheduler
    setup_scheduler(application)  # dentro de post_init
"""

import logging
from datetime import date, datetime, timedelta
from typing import Set
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from src.bot.api_client import ThdoraApiClient

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None
_subscribed_users: Set[int] = set()
api = ThdoraApiClient()

_DEFAULT_TZ = "Europe/Madrid"
_DEFAULT_SUMMARY_TIME = "08:00"
_DEFAULT_EVENING_TIME = "22:00"
_DEFAULT_OFFSETS = [60, 30, 15]


# ── Singleton ────────────────────────────────────────────────

def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


# ── Gestión de usuarios suscritos ────────────────────────────────

def _validate_user_id(user_id: int) -> None:
    if not user_id or user_id <= 0:
        raise ValueError("user_id es obligatorio y debe ser > 0")


def subscribe_user(user_id: int) -> None:
    """Suscribir usuario al scheduler (llamar en cmd_start)."""
    _validate_user_id(user_id)
    _subscribed_users.add(user_id)
    logger.info("✅ Usuario %d suscrito al scheduler", user_id)


def unsubscribe_user(user_id: int) -> None:
    """Desuscribir usuario del scheduler."""
    _subscribed_users.discard(user_id)
    logger.info("❌ Usuario %d desuscrito del scheduler", user_id)


def get_subscribed_users() -> Set[int]:
    """Retorna copia del set de usuarios suscritos."""
    return set(_subscribed_users)


# ── Setup desde main.py ────────────────────────────────────────

async def setup_scheduler(app) -> None:
    """
    Arrancar el scheduler desde post_init de PTB.
    app → objeto Application de python-telegram-bot.
    """
    scheduler = get_scheduler()
    if scheduler.running:
        return
    scheduler.start()
    logger.info("⏰ Scheduler F12 iniciado (multi-usuario)")


# ── Programar jobs de un usuario ────────────────────────────────

def schedule_user_jobs(bot, user_id: int, cfg: dict) -> None:
    """
    Programa (o reprograma) los dos jobs diarios del usuario.
    Se llama desde cmd_start y cuando el usuario cambia horarios en config.
    """
    _validate_user_id(user_id)
    subscribe_user(user_id)
    scheduler = get_scheduler()
    tz = cfg.get("timezone", _DEFAULT_TZ)

    if cfg.get("daily_summary_enabled", True):
        summary_time = cfg.get("daily_summary_time", _DEFAULT_SUMMARY_TIME)
        h, m = map(int, summary_time.split(":"))
        job_id = f"daily_summary_{user_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        scheduler.add_job(
            _send_daily_summary,
            CronTrigger(hour=h, minute=m, timezone=tz),
            id=job_id,
            kwargs={"bot": bot, "user_id": user_id},
            misfire_grace_time=300,
        )
        logger.info("⏰ daily_summary_%d programado a las %s", user_id, summary_time)

    if cfg.get("evening_log_enabled", True):
        evening_time = cfg.get("evening_log_time", _DEFAULT_EVENING_TIME)
        h, m = map(int, evening_time.split(":"))
        job_id = f"evening_log_{user_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        scheduler.add_job(
            _send_evening_log,
            CronTrigger(hour=h, minute=m, timezone=tz),
            id=job_id,
            kwargs={"bot": bot, "user_id": user_id},
            misfire_grace_time=300,
        )
        logger.info("⏰ evening_log_%d programado a las %s", user_id, evening_time)


# ── Jobs de cita (one-shot) ───────────────────────────────────────

def schedule_apt_reminders(bot, user_id: int, apt: dict, cfg: dict) -> None:
    """
    Programa avisos one-shot para una cita según notif_offsets del usuario.
    apt puede tener la fecha como 'date' o 'date_str'.
    """
    _validate_user_id(user_id)
    if not cfg.get("notif_enabled", True):
        return

    scheduler = get_scheduler()
    tz = ZoneInfo(cfg.get("timezone", _DEFAULT_TZ))
    date_str = apt.get("date") or apt.get("date_str", "")
    time_str = apt.get("time", "")
    apt_id = apt.get("id", apt.get("index", 0))
    offsets = cfg.get("notif_offsets", _DEFAULT_OFFSETS)

    if not date_str or not time_str:
        logger.warning("schedule_apt_reminders: apt sin date o time: %s", apt)
        return

    apt_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)

    for offset in offsets:
        try:
            offset_min = int(offset)
        except (ValueError, TypeError):
            continue
        fire_at = apt_dt - timedelta(minutes=offset_min)
        if fire_at <= datetime.now(tz=tz):
            continue
        job_id = f"apt_reminder_{user_id}_{apt_id}_{offset_min}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        scheduler.add_job(
            _send_apt_reminder,
            DateTrigger(run_date=fire_at),
            id=job_id,
            kwargs={"bot": bot, "user_id": user_id, "apt": apt, "minutes": offset_min},
        )
        logger.info("⏰ apt_reminder %s → %s (-%dmin)", job_id, fire_at, offset_min)


def cancel_apt_reminders(user_id: int, apt_id: int) -> None:
    """Cancela todos los avisos pendientes de una cita."""
    _validate_user_id(user_id)
    scheduler = get_scheduler()
    for job in scheduler.get_jobs():
        if job.id.startswith(f"apt_reminder_{user_id}_{apt_id}_"):
            scheduler.remove_job(job.id)
            logger.info("❌ apt_reminder cancelado: %s", job.id)


# ── Funciones de envío ───────────────────────────────────────────

async def _send_daily_summary(bot, user_id: int) -> None:
    """Envía el resumen de citas del día al usuario."""
    try:
        today = str(date.today())
        data = await api.get_summary(today, user_id=user_id)
        apts = data.get("appointments", [])
        if not apts:
            text = "🌅 *Buenos días\!*\n\nHoy no tienes citas programadas\. Que sea un día tranquilo 🏡"
        else:
            lines = [f"🌅 *Buenos días\! Tus citas de hoy \({today}\):*\n"]
            for apt in apts:
                nombre = apt.get("name") or apt.get("type", "cita")
                lines.append(f"  ⏰ *{apt['time']}* \u2014 {nombre}")
            text = "\n".join(lines)
        await bot.send_message(chat_id=user_id, text=text, parse_mode="MarkdownV2")
        logger.info("✅ daily_summary enviado a %d", user_id)
    except Exception as e:
        logger.error("Error en daily_summary para %d: %s", user_id, e)


async def _send_evening_log(bot, user_id: int) -> None:
    """Recuerda al usuario que registre sus hábitos del día."""
    try:
        today = str(date.today())
        habits = await api.get_habits(today, user_id=user_id)
        if not habits:
            text = (
                "🌙 *Última llamada del día\!*\n\n"
                "Todavía no has registrado ningún hábito hoy\. "
                "¿Apuntamos algo antes de dormir? Usa /habito"
            )
        else:
            hab_list = "\n".join(f"  \u2022 *{k}*: {v}" for k, v in habits.items())
            text = (
                f"🌙 *Resumen de hábitos \u2014 {today}*\n\n"
                f"{hab_list}\n\n"
                f"¿Falta algo por apuntar? Usa /habito"
            )
        await bot.send_message(chat_id=user_id, text=text, parse_mode="MarkdownV2")
        logger.info("✅ evening_log enviado a %d", user_id)
    except Exception as e:
        logger.error("Error en evening_log para %d: %s", user_id, e)


async def _send_apt_reminder(bot, user_id: int, apt: dict, minutes: int) -> None:
    """Avisa al usuario X minutos antes de una cita."""
    try:
        nombre = apt.get("name") or apt.get("type", "cita")
        tiempo = f"{minutes // 60}h" if minutes >= 60 else f"{minutes} min"
        text = (
            f"🔔 *Recordatorio*\n\n"
            f"En *{tiempo}* tienes:\n"
            f"  ⏰ *{apt['time']}* \u2014 {nombre}"
        )
        await bot.send_message(chat_id=user_id, text=text, parse_mode="MarkdownV2")
        logger.info("✅ apt_reminder enviado a %d (-%dmin cita %s)", user_id, minutes, apt.get('id'))
    except Exception as e:
        logger.error("Error en apt_reminder para %d: %s", user_id, e)
