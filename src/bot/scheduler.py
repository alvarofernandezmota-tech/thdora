import asyncio
import logging
from datetime import datetime, timedelta

import httpx
from telegram.ext import Application

from src.config import settings

logger = logging.getLogger(__name__)

_OLLAMA_HEALTH_TIMEOUT = httpx.Timeout(5.0)


class Scheduler:
    def __init__(self, app: Application, api_client, user_ids: list[int]):
        self.app = app
        self.api = api_client
        self.user_ids = user_ids

    async def start(self) -> None:
        # Sprint 4: alerta si Ollama está caído al arrancar (no bloquea)
        asyncio.create_task(self._check_ollama_on_startup())
        asyncio.create_task(self._loop_reminders())
        asyncio.create_task(self._loop_morning_summary())

    async def _check_ollama_on_startup(self) -> None:
        """Si LLM_BACKEND=ollama, comprueba salud de Ollama y avisa al owner si está caído."""
        if getattr(settings, "LLM_BACKEND", "groq").lower() != "ollama":
            return

        owner_id = getattr(settings, "OWNER_TELEGRAM_ID", 0)
        ollama_host = getattr(settings, "OLLAMA_HOST", "http://localhost:11434")

        try:
            async with httpx.AsyncClient(timeout=_OLLAMA_HEALTH_TIMEOUT) as client:
                resp = await client.get(f"{ollama_host}/api/tags")
            if resp.status_code == 200:
                logger.info("Ollama health check OK en %s", ollama_host)
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
            logger.warning("OWNER_TELEGRAM_ID no configurado, no se puede enviar alerta Ollama")
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
