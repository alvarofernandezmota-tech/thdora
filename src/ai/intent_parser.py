"""
Parser de intenciones para THDORA.

Transforma mensajes de lenguaje natural en acciones estructuradas
que el bot puede ejecutar directamente.

Intenciones detectadas::

    ver_citas       → {"date": "YYYY-MM-DD"}
    crear_cita      → {"date", "time", "name", "type", "notes"}
    ver_habitos     → {"date": "YYYY-MM-DD"}
    registrar_habito→ {"date", "habit", "value"}
    ver_resumen     → {"date": "YYYY-MM-DD"}
    chat            → {"reply": "texto libre"} — respuesta directa sin acción
    desconocido     → {} — no se entendió

Uso::

    from src.ai.intent_parser import parse_intent
    result = await parse_intent("Añade cita el martes a las 10 con el dentista")
    # {"intent": "crear_cita", "date": "2026-03-31", "time": "10:00", "name": "Dentista", ...}
"""

import json
import logging
from datetime import date, timedelta
from typing import Any, Dict

from src.ai.groq_client import GroqClient, GroqError, get_groq_client

logger = logging.getLogger(__name__)

_today = lambda: str(date.today())  # noqa: E731

_INTENT_SYSTEM = """
Eres el motor de intenciones de THDORA, un asistente personal.
Debes analizar el mensaje del usuario y devolver EXCLUSIVAMENTE un JSON válido.

Fecha de hoy: {today}

Intenciones posibles y su formato JSON:

1. ver_citas
   {{"intent": "ver_citas", "date": "YYYY-MM-DD"}}

2. crear_cita
   {{"intent": "crear_cita", "date": "YYYY-MM-DD", "time": "HH:MM", "name": "...", "type": "médica|personal|trabajo|otra", "notes": ""}}

3. ver_habitos
   {{"intent": "ver_habitos", "date": "YYYY-MM-DD"}}

4. registrar_habito
   {{"intent": "registrar_habito", "date": "YYYY-MM-DD", "habit": "...", "value": "..."}}

5. ver_resumen
   {{"intent": "ver_resumen", "date": "YYYY-MM-DD"}}

6. chat (pregunta general, conversación, o no es una acción concreta)
   {{"intent": "chat", "reply": "tu respuesta directa aquí"}}

7. desconocido
   {{"intent": "desconocido"}}

Reglas:
- Si el usuario dice "hoy", usa la fecha de hoy.
- Si dice "mañana", suma 1 día. Si dice "ayer", resta 1.
- Si no se menciona fecha, asume hoy.
- Si no hay hora en crear_cita, pon "00:00".
- Si no hay tipo de cita, pon "otra".
- SOLO devuelves JSON, sin texto extra, sin markdown, sin ```.
"""


async def parse_intent(user_message: str) -> Dict[str, Any]:
    """
    Detecta la intención del mensaje y devuelve un dict estructurado.

    Args:
        user_message: Texto libre del usuario.

    Returns:
        Dict con al menos la clave ``intent``.
        Nunca lanza excepción — en caso de error devuelve intent=desconocido.
    """
    today = _today()
    system = _INTENT_SYSTEM.format(today=today)

    client = get_groq_client()
    # Usamos un cliente temporal con system prompt de intenciones
    intent_client = GroqClient(
        api_key=client.api_key,
        model=client.model,
        system_prompt=system,
    )

    try:
        raw = await intent_client.ask(
            user_message,
            temperature=0.1,   # bajo para respuestas deterministas
            max_tokens=256,
        )
        # Limpiar por si el modelo añade algo antes/después del JSON
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        if "intent" not in data:
            return {"intent": "desconocido"}
        return data
    except (GroqError, json.JSONDecodeError, Exception) as exc:
        logger.warning("parse_intent error: %s | raw: %s", exc, locals().get("raw", ""))
        return {"intent": "desconocido"}
