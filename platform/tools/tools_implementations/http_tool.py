import httpx
from tools.registry import register


@register("tools.http.request")
async def request(url: str, method: str = "GET", payload: dict = None) -> str:
    """Realiza una petición HTTP genérica."""
    async with httpx.AsyncClient(timeout=10) as client:
        if method.upper() == "GET":
            resp = await client.get(url)
        else:
            resp = await client.post(url, json=payload or {})
    return resp.text[:2000]  # limita respuesta para el LLM
