import asyncio
import logging
from datetime import datetime, timedelta

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

from src.config import settings

logger = logging.getLogger(__name__)

_OLLAMA_HEALTH_TIMEOUT = httpx.Timeout(5.0)

# ── Singleton APScheduler ─────────────────────────────────────────────────
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """Devuelve (o crea) el scheduler global AsyncIO de APScheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Europe/Madrid")
    return _scheduler


# ── Helpers de recordatorio por cita (usados por citas.py) ───────────────

def _reminder_job_ids(user_id: str, apt_id) -> list[str]:
    return [
        f"reminder_30_{user_id}_{apt_id}",
        f"reminder_0_{user_id}_{apt_id}",
    ]


async def _send_reminder(bot, user_id: str, text: str) -> None:
    try:
        await bot.send_message(chat_id=int(user_id), text=text, parse_mode="Markdown")
    except Exception as exc:
        logger.warning("No se pudo enviar reminder a %s: %s", user_id, exc)


def schedule_apt_reminders(bot, user_id: str, apt: dict, cfg: dict) -> None:
    """
    Programa recordatorios APScheduler para una cita (30 min antes + momento exacto).
    Respeta cfg.notifications_enabled.
    """
    if not cfg.get("notifications_enabled", True):
        return

    date_str = apt.get("date") or apt.get("date_str", "")
    time_str = apt.get("time", "")
    if not date_str or not time_str:
        logger.warning("schedule_apt_reminders: datos incompletos apt=%s", apt)
        return

    try:
        apt_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        logger.warning("schedule_apt_reminders: formato inválido %s %s", date_str, time_str)
        return

    nombre = apt.get("name") or apt.get("type", "cita")
    apt_id = apt.get("index", apt.get("id", f"{date_str}_{time_str}"))
    scheduler = get_scheduler()
    now = datetime.now()

    run_at_30 = apt_dt - timedelta(minutes=30)
    job_id_30 = f"reminder_30_{user_id}_{apt_id}"
    if run_at_30 > now:
        scheduler.add_job(
            _send_reminder, trigger="date", run_date=run_at_30,
            args=[bot, user_id, f"⏰ *Recordatorio* — en 30 min tienes: *{nombre}* a las {time_str}"],
            id=job_id_30, replace_existing=True, misfire_grace_time=120,
        )

    job_id_0 = f"reminder_0_{user_id}_{apt_id}"
    if apt_dt > now:
        scheduler.add_job(
            _send_reminder, trigger="date", run_date=apt_dt,
            args=[bot, user_id, f"🔔 *Ahora tienes:* *{nombre}*"],
            id=job_id_0, replace_existing=True, misfire_grace_time=120,
        )


def cancel_apt_reminders(user_id: str, apt_id) -> None:
    """Cancela los jobs de recordatorio de una cita."""
    scheduler = get_scheduler()
    for job_id in _reminder_job_ids(user_id, apt_id):
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass


# ── Jobs diarios por usuario (usado por config.py) ───────────────────────

async def _send_daily_summary(bot, user_id: str) -> None:
    """Envía el resumen diario al usuario."""
    try:
        await bot.send_message(
            chat_id=int(user_id),
            text="☀️ *Resumen diario THDORA*\n\nUsa /citas para ver tu agenda de hoy.",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.warning("No se pudo enviar resumen diario a %s: %s", user_id, exc)


async def _send_evening_log(bot, user_id: str) -> None:
    """Envía el evening log al usuario."""
    try:
        await bot.send_message(
            chat_id=int(user_id),
            text="🌙 *Evening log THDORA*\n\nUsa /habitos para registrar tu progreso de hoy.",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.warning("No se pudo enviar evening log a %s: %s", user_id, exc)


def schedule_user_jobs(bot, user_id: str, cfg: dict) -> None:
    """
    (Re)programa los jobs diarios de un usuario según su configuración.

    - Resumen diario: si cfg.daily_summary_enabled, a cfg.daily_summary_time
    - Evening log:    si cfg.evening_log_enabled,   a cfg.evening_log_time

    Siempre cancela los jobs previos antes de reprogramar para evitar duplicados.

    Args:
        bot:     Instancia de telegram.Bot.
        user_id: ID Telegram del usuario como str.
        cfg:     Dict de configuración del usuario obtenido de la API.
    """
    scheduler = get_scheduler()

    # ── Resumen diario ──────────────────────────────────────────────────
    job_id_summary = f"daily_summary_{user_id}"
    try:
        scheduler.remove_job(job_id_summary)
    except Exception:
        pass

    if cfg.get("daily_summary_enabled", True):
        hora_str = cfg.get("daily_summary_time", "08:00")
        try:
            h, m = hora_str.split(":")
            scheduler.add_job(
                _send_daily_summary,
                trigger="cron",
                hour=int(h), minute=int(m),
                args=[bot, user_id],
                id=job_id_summary,
                replace_existing=True,
                misfire_grace_time=300,
            )
            logger.info("Resumen diario programado para %s a las %s", user_id, hora_str)
        except Exception as exc:
            logger.warning("No se pudo programar resumen diario %s: %s", user_id, exc)

    # ── Evening log ─────────────────────────────────────────────────────
    job_id_evening = f"evening_log_{user_id}"
    try:
        scheduler.remove_job(job_id_evening)
    except Exception:
        pass

    if cfg.get("evening_log_enabled", True):
        hora_str = cfg.get("evening_log_time", "21:00")
        try:
            h, m = hora_str.split(":")
            scheduler.add_job(
                _send_evening_log,
                trigger="cron",
                hour=int(h), minute=int(m),
                args=[bot, user_id],
                id=job_id_evening,
                replace_existing=True,
                misfire_grace_time=300,
            )
            logger.info("Evening log programado para %s a las %s", user_id, hora_str)
        except Exception as exc:
            logger.warning("No se pudo programar evening log %s: %s", user_id, exc)


# ── Scheduler de Telegram (polling + resumen mañana) ─────────────────────

class Scheduler:
    def __init__(self, app: Application, api_client, user_ids: list[int]):
        self.app = app
        self.api = api_client
        self.user_ids = user_ids

    async def start(self) -> None:
        asyncio.create_task(self._check_ollama_on_startup())
        asyncio.create_task(self._loop_reminders())
        asyncio.create_task(self._loop_morning_summary())

    async def _check_ollama_on_startup(self) -> None:
        if getattr(settings, "LLM_BACKEND", "groq").lower() != "ollama":
            return
        owner_id = getattr(settings, "OWNER_TELEGRAM_ID", 0)
        ollama_host = getattr(settings, "OLLAMA_HOST", "http://localhost:11434")
        try:
            async with httpx.AsyncClient(timeout=_OLLAMA_HEALTH_TIMEOUT) as client:
                resp = await client.get(f"{ollama_host}/api/tags")
            if resp.status_code == 200:
                return
            motivo = f"HTTP {resp.status_code}"
        except httpx.TimeoutException:
            motivo = "timeout (>5s)"
        except httpx.ConnectError:
            motivo = "conexión rechazada"
        except Exception as exc:
            motivo = str(exc) or type(exc).__name__
        logger.warning("Ollama no responde al arrancar: %s", motivo)
        if not owner_id:
            return
        try:
            await self.app.bot.send_message(
                chat_id=owner_id,
                text=(
                    f"⚠️ *THDORA — Ollama caído al arrancar*\n\n"
                    f"🔴 Motivo: `{motivo}`\n"
                    f"🌐 Host: `{ollama_host}`\n\n"
                    f"El bot arrancó con fallback a Groq."
                ),
                parse_mode="Markdown",
            )
        except Exception as exc:
            logger.error("No se pudo enviar alerta Ollama al owner: %s", exc)

    async def _loop_reminders(self) -> None:
        while True:
            try:
                await self._check_upcoming_appointments()
            except Exception as e:
                logger.error("Scheduler reminder error: %s", e)
            await asyncio.sleep(60)

    async def _check_upcoming_appointments(self) -> None:
        now = datetime.now()
        target = now + timedelta(minutes=30)
        target_str = target.strftime("%H:%M")
        for user_id in self.user_ids:
            try:
                citas = await self.api.get_appointments_today(user_id)
                name = await self.api.get_user_name(user_id)
                for cita in citas:
                    hora = cita.get("hora", "")
                    if hora[:5] == target_str and not cita.get("reminded", False):
                        titulo = cita.get("titulo") or cita.get("descripcion") or "tu cita"
                        lugar = cita.get("lugar", "")
                        texto = (
                            f"⏰ {name}, en 30 minutos tienes: *{titulo}*."
                            + (f"\n📍 {lugar}" if lugar else "")
                        )
                        await self.app.bot.send_message(chat_id=user_id, text=texto, parse_mode="Markdown")
            except Exception as e:
                logger.warning("Reminder error user %s: %s", user_id, e)

    async def _loop_morning_summary(self) -> None:
        while True:
            now = datetime.now()
            target = now.replace(hour=8, minute=0, second=0, microsecond=0)
            if now >= target:
                target += timedelta(days=1)
            await asyncio.sleep((target - now).total_seconds())
            try:
                await self._send_morning_summary()
            except Exception as e:
                logger.error("Morning summary error: %s", e)

    async def _send_morning_summary(self) -> None:
        day_label = datetime.now().strftime("%A %d de %B").capitalize()
        for user_id in self.user_ids:
            try:
                citas = await self.api.get_appointments_today(user_id)
                name = await self.api.get_user_name(user_id)
                if not citas:
                    texto = (
                        f"☀️ Buenos dias, *{name}*.\n\n"
                        f"Hoy es {day_label} y no tienes citas programadas.\n"
                        "Buen momento para añadir algo con /citas! 📅"
                    )
                else:
                    lineas = "\n".join(
                        f"  • {c.get('hora', '??:??')} — {c.get('titulo') or c.get('descripcion', 'Cita')}"
                        for c in sorted(citas, key=lambda x: x.get("hora", ""))
                    )
                    texto = (
                        f"☀️ Buenos dias, *{name}*.\n\n"
                        f"Tu agenda para hoy ({day_label}):\n\n"
                        f"{lineas}\n\n"
                        "Que vaya bien el dia! 💪"
                    )
                await self.app.bot.send_message(chat_id=user_id, text=texto, parse_mode="Markdown")
            except Exception as e:
                logger.warning("Morning summary error user %s: %s", user_id, e)
