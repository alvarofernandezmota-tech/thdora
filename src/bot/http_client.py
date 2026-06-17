"""Cliente httpx compartido — singleton para toda la aplicación."""
from __future__ import annotations

import httpx

_client: httpx.AsyncClient | None = None

_LIMITS = httpx.Limits(max_connections=20, max_keepalive_connections=10)
_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


def get_client() -> httpx.AsyncClient:
    """Devuelve el cliente httpx compartido, creándolo si no existe o está cerrado."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(limits=_LIMITS, timeout=_TIMEOUT)
    return _client


async def close_client() -> None:
    """Cierra el cliente compartido limpiamente (llamar en shutdown)."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
