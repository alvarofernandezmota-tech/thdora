"""Handler /tiempo — consulta el tiempo actual via OpenWeatherMap API gratuita."""
from __future__ import annotations

import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.middleware import require_allowed_user
from src.config import settings

logger = logging.getLogger(__name__)

_OWM_URL = "https://api.openweathermap.org/data/2.5/weather"
_TIMEOUT = httpx.Timeout(10.0)


@require_allowed_user
async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /tiempo [ciudad] — muestra temperatura y descripción del tiempo."""
    if not update.message:
        return

    ciudad = " ".join(context.args).strip() if context.args else ""

    if not ciudad:
        await update.message.reply_text(
            "🌍 ¿De qué ciudad quieres saber el tiempo?\n"
            "Uso: /tiempo <ciudad>\n"
            "Ejemplo: /tiempo Sevilla"
        )
        return

    if not settings.OWM_API_KEY:
        logger.error("OWM_API_KEY no configurada")
        await update.message.reply_text(
            "⚙️ El servicio de tiempo no está configurado. "
            "Falta la clave OWM_API_KEY en el servidor."
        )
        return

    params = {
        "q": ciudad,
        "appid": settings.OWM_API_KEY,
        "units": "metric",
        "lang": "es",
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(_OWM_URL, params=params)

        if resp.status_code == 404:
            await update.message.reply_text(
                f"❓ No encontré la ciudad *{ciudad}*. "
                "Comprueba el nombre e inténtalo de nuevo.",
                parse_mode="Markdown",
            )
            return

        if resp.status_code == 401:
            logger.error("OWM_API_KEY inválida o sin permisos")
            await update.message.reply_text(
                "🔑 La clave de la API del tiempo no es válida. "
                "Contacta con el administrador."
            )
            return

        resp.raise_for_status()
        data = resp.json()

        nombre_ciudad = data.get("name", ciudad)
        pais = data.get("sys", {}).get("country", "")
        temp = data["main"]["temp"]
        sensacion = data["main"]["feels_like"]
        descripcion = data["weather"][0]["description"].capitalize()
        humedad = data["main"]["humidity"]

        texto = (
            f"🌤 *{nombre_ciudad}{', ' + pais if pais else ''}*\n\n"
            f"🌡 Temperatura: *{temp:.1f}°C*\n"
            f"🤔 Sensación: {sensacion:.1f}°C\n"
            f"💧 Humedad: {humedad}%\n"
            f"📝 {descripcion}"
        )
        await update.message.reply_text(texto, parse_mode="Markdown")

    except httpx.TimeoutException:
        logger.warning("OpenWeatherMap timeout para ciudad=%s", ciudad)
        await update.message.reply_text("⏳ El servicio de tiempo tardó demasiado. Inténtalo de nuevo.")
    except httpx.HTTPStatusError as exc:
        logger.error("OWM HTTP error %s para ciudad=%s", exc.response.status_code, ciudad)
        await update.message.reply_text("❌ Error consultando el tiempo. Inténtalo más tarde.")
    except Exception as exc:
        logger.error("Error inesperado weather_handler ciudad=%s: %s", ciudad, exc)
        await update.message.reply_text("❌ Ocurrió un error consultando el tiempo.")
