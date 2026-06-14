import httpx
from core.config import settings
from tools.registry import register


@register("tools.telegram.send_message")
async def send_message(chat_id: str, text: str) -> str:
    """Envía un mensaje a un chat de Telegram vía Bot API."""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text})
        resp.raise_for_status()
    return f"Mensaje enviado a {chat_id}"
