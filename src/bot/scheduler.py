"""
Scheduler de notificaciones proactivas — F12.

Jobs:
    daily_summary   → resumen de citas del día (hora configurable, default 08:00)
    evening_log     → recordatorio de hábitos del día (hora configurable, default 22:00)
    apt_reminder_*  → aviso X min antes de cada cita (one-shot, ids dinámicos)

Arquitectura:
    - Un único AsyncIOScheduler compartido (singleton)
    - Los jobs diarios se programan al arrancar y se reprograman si el usuario
      cambia la hora en /config → Notificaciones
    - Los jobs one-shot de cita se programan al crear la cita y se cancelan
      al borrarla o reprograman al editarla
    - Todos los jobs leen la config del usuario en el momento de ejecutarse
      (no al programarse) para respetar cambios de config en caliente

Uso::

    from src.bot.scheduler import get_scheduler, start_scheduler
    scheduler = get_scheduler()
    await start_scheduler(app, scheduler)
"""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from src.bot.api_client import ThdoraApiClient

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None
api = ThdoraApiClient()

_DEFAULT_TZ = "Europe/Madrid"


# ── Singleton ────────────────────────────────────────────────

def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


# ── Arranque ───────────────────────────────────────────────

async def start_scheduler(app, bot_app) -> None:
    """
    Arranca el scheduler y programa los jobs fijos del primer usuario.
    Se llama desde main.py después de construir la app de Telegram.

    app      → objeto Application de python-telegram-bot (para bot.send_message)
    bot_app  → el mismo objeto (alias para claridad)
    """
    scheduler = get_scheduler()
    if scheduler.running:
        return
    scheduler.start()
    logger.info("⏰ Scheduler iniciado")


# ── Programar jobs de un usuario ─────────────────────────────────

def schedule_user_jobs(bot, user_id: str, cfg: dict) -> None:
    """
    Programa (o reprograma) los dos jobs diarios del usuario:
        - daily_summary_{user_id}
        - evening_log_{user_id}
    Si el job ya existe, lo reemplaza con la nueva hora.
    """
    scheduler = get_scheduler()
    tz = cfg.get("timezone", _DEFAULT_TZ)

    # ─ Resumen diario ────────────────────────────────────────
    if cfg.get("daily_summary_enabled", True):
        summary_time = cfg.get("daily_summary_time", "08:00")
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
        logger.info("⏰ daily_summary_%s programado a las %s", user_id, summary_time)

    # ─ Evening log ──────────────────────────────────────────
    if cfg.get("evening_log_enabled", True):
        evening_time = cfg.get("evening_log_time", "22:00")
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
        logger.info("⏰ evening_log_%s programado a las %s", user_id, evening_time)


# ── Jobs de cita (one-shot) ───────────────────────────────────────

def schedule_apt_reminders(bot, user_id: str, apt: dict, cfg: dict) -> None:
    """
    Programa avisos one-shot para una cita según notif_offsets del usuario.
    Si la hora ya pasó, no programa nada (APScheduler lo ignoraría de todas formas).
    """
    if not cfg.get("notif_enabled", True):
        return

    scheduler  = get_scheduler()
    tz         = ZoneInfo(cfg.get("timezone", _DEFAULT_TZ))
    date_str   = apt["date"]
    time_str   = apt["time"]
    apt_id     = apt.get("id", apt.get("index", 0))
    offsets    = cfg.get("notif_offsets", ["60", "30", "15"])
    apt_dt     = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)

    for offset_str in offsets:
        try:
            offset_min = int(offset_str)
        except ValueError:
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
            kwargs={
                "bot":      bot,
                "user_id":  user_id,
                "apt":      apt,
                "minutes":  offset_min,
            },
        )
        logger.info("⏰ apt_reminder %s → %s (-% dmin)", job_id, fire_at, offset_min)


def cancel_apt_reminders(user_id: str, apt_id: int) -> None:
    """Cancela todos los avisos pendientes de una cita."""
    scheduler = get_scheduler()
    for job in scheduler.get_jobs():
        if job.id.startswith(f"apt_reminder_{user_id}_{apt_id}_"):
            scheduler.remove_job(job.id)
            logger.info("❌ apt_reminder cancelado: %s", job.id)


# ── Funciones de envío ────────────────────────────────────────────

async def _send_daily_summary(bot, user_id: str) -> None:
    """Envía el resumen de citas del día al usuario."""
    try:
        cfg = await api.get_user_config(user_id)
        if not cfg.get("daily_summary_enabled", True):
            return
        from datetime import date
        today = str(date.today())
        data  = await api.get_summary(today)
        apts  = data.get("appointments", [])
        if not apts:
            text = f"🌅 *Buenos días\!*\n\nHoy no tienes citas programadas\. Que sea un día tranquilo 🏡"
        else:
            lines = [f"🌅 *Buenos días\! Tus citas de hoy \({today}\):*\n"]
            for apt in apts:
                nombre = apt.get("name") or apt.get("type", "cita")
                lines.append(f"  ⏰ *{apt['time']}* \u2014 {nombre}")
            text = "\n".join(lines)
        await bot.send_message(chat_id=int(user_id), text=text, parse_mode="MarkdownV2")
        logger.info("✅ daily_summary enviado a %s", user_id)
    except Exception as e:
        logger.error("Error en daily_summary para %s: %s", user_id, e)


async def _send_evening_log(bot, user_id: str) -> None:
    """Recuerda al usuario que registre sus hábitos del día."""
    try:
        cfg = await api.get_user_config(user_id)
        if not cfg.get("evening_log_enabled", True):
            return
        from datetime import date
        today  = str(date.today())
        habits = await api.get_habits(today)
        n      = len(habits)
        if n == 0:
            text = (
                f"🌙 *Última llamada del día\!*\n\n"
                f"Todavía no has registrado ningún hábito hoy\."
                f" ¿Apuntamos algo antes de dormir? Usa /habito"
            )
        else:
            hab_list = "\n".join(f"  • *{k}*: {v}" for k, v in habits.items())
            text = (
                f"🌙 *Resumen de hábitos \u2014 {today}*\n\n"
                f"{hab_list}\n\n"
                f"¿Falta algo por apuntar? Usa /habito"
            )
        await bot.send_message(chat_id=int(user_id), text=text, parse_mode="MarkdownV2")
        logger.info("✅ evening_log enviado a %s", user_id)
    except Exception as e:
        logger.error("Error en evening_log para %s: %s", user_id, e)


async def _send_apt_reminder(bot, user_id: str, apt: dict, minutes: int) -> None:
    """Avisa al usuario X minutos antes de una cita."""
    try:
        nombre = apt.get("name") or apt.get("type", "cita")
        if minutes >= 60:
            tiempo = f"{minutes // 60}h"
        else:
            tiempo = f"{minutes} min"
        text = (
            f"🔔 *Recordatorio*\n\n"
            f"En *{tiempo}* tienes:\n"
            f"  ⏰ *{apt['time']}* \u2014 {nombre}"
        )
        await bot.send_message(chat_id=int(user_id), text=text, parse_mode="MarkdownV2")
        logger.info("✅ apt_reminder enviado a %s (-% dmin cita %s)", user_id, minutes, apt.get('id'))
    except Exception as e:
        logger.error("Error en apt_reminder para %s: %s", user_id, e)
