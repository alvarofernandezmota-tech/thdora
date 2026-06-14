"""
Construye el bloque de contexto dinámico para inyectar en el system prompt de Groq.

Llama a la API interna de THDORA para obtener citas y hábitos reales del día.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)

_API_BASE = os.getenv("THDORA_API_URL", "http://localhost:8000")
_TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)


async def _safe_get(url: str) -> Any:
    """GET a la API interna; devuelve None en cualquier fallo."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(url)
            if r.is_error:
                return None
            return r.json()
    except Exception as exc:
        logger.warning("context_builder: error en GET %s — %s", url, exc)
        return None


async def build_context_block(api_base_url: str = _API_BASE, date: str = "") -> str:
    """
    Genera un bloque de texto con las citas y hábitos del usuario para la fecha dada.

    Args:
        api_base_url: URL base de la API interna (por defecto THDORA_API_URL).
        date:         Fecha en formato YYYY-MM-DD. Si está vacía usa hoy.

    Returns:
        String formateado listo para inyectar al final del system prompt.
        Ejemplo:
            === CONTEXTO DEL USUARIO HOY (2026-06-15) ===
            Citas: 10:00 Dentista, 17:30 Gym
            Hábitos activos: sueño: 7 horas, agua: 2L
    """
    from datetime import date as date_cls

    if not date:
        date = date_cls.today().isoformat()

    base = api_base_url.rstrip("/")

    appointments_raw, habits_raw = await asyncio.gather(
        _safe_get(f"{base}/appointments/{date}"),
        _safe_get(f"{base}/habits/{date}"),
    )

    appointments: List[Dict] = appointments_raw or []
    if appointments:
        citas_str = ", ".join(
            f"{c.get('time', '?')} {c.get('name', '?')}" for c in appointments
        )
    else:
        citas_str = "Sin citas hoy"

    habits_list: List[Dict] = habits_raw or []
    if habits_list:
        habs_str = ", ".join(
            f"{h.get('habit', '?')}: {h.get('value', '?')}" for h in habits_list
        )
    else:
        habs_str = "Sin hábitos configurados"

    return (
        f"=== CONTEXTO DEL USUARIO HOY ({date}) ===\n"
        f"Citas: {citas_str}\n"
        f"Hábitos activos: {habs_str}"
    )
