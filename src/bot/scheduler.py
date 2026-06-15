import asyncio
import logging
from datetime import datetime, timedelta
from telegram.ext import Application
from src.bot.api_client import ApiClient

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, app: Application, api_client: ApiClient, user_ids: list[int]):
        self.app = app
        self.api = api_client
        self.user_ids = user_ids

    async def start(self) -> None:
        asyncio.create_task(self._loop_reminders())
        asyncio.create_task(self._loop_morning_summary())

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
                        await self.app.bot.send_message(
                            chat_id=user_id,
                            text=texto,
                            parse_mode="Markdown",
                        )
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

                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=texto,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.warning("Morning summary error user %s: %s", user_id, e)
