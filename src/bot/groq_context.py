"""Construcción de contexto dinámico para inyectar en llamadas al LLM."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_DIAS_ES = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"}
_MESES_ES = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun", 7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}


def _format_hora_actual() -> str:
    now = datetime.now()
    dia = _DIAS_ES[now.weekday()]
    mes = _MESES_ES[now.month]
    return f"Son las {now.strftime('%H:%M')} del {dia} {now.day} {mes}"


def _format_citas(citas: list[dict]) -> str:
    if not citas:
        return "ninguna"
    return ", ".join(f"{c.get('hora', '??:??')} {c.get('nombre', c.get('title', 'Cita'))}" for c in citas)


def _format_habitos(habitos: list[dict]) -> str:
    if not habitos:
        return "ninguno"
    partes = []
    for h in habitos:
        nombre = h.get("nombre", h.get("name", "Hábito"))
        completado = h.get("completado_hoy", h.get("done_today", False))
        partes.append(f"{'✅' if completado else '⬜'} {nombre}")
    return " ".join(partes)


async def build_context(user_id: int, api_client: object) -> str:
    """Construye el contexto dinámico del usuario para el LLM."""
    try:
        hoy = datetime.now().strftime("%Y-%m-%d")
        citas, habitos = await asyncio.gather(
            api_client.get_appointments(user_id=user_id, fecha=hoy),
            api_client.get_habits(user_id=user_id, solo_activos=True),
            return_exceptions=True,
        )
        citas_list: list[dict] = citas if not isinstance(citas, BaseException) else []
        habitos_list: list[dict] = habitos if not isinstance(habitos, BaseException) else []
        if isinstance(citas, BaseException):
            logger.warning("Error obteniendo citas para contexto: %s", citas)
        if isinstance(habitos, BaseException):
            logger.warning("Error obteniendo hábitos para contexto: %s", habitos)
        return (
            f"{_format_hora_actual()}\n"
            f"CITAS HOY: {_format_citas(citas_list)}\n"
            f"HÁBITOS: {_format_habitos(habitos_list)}"
        )
    except Exception as exc:
        logger.warning("Fallo general al construir contexto para user_id=%s: %s", user_id, exc)
        return ""
