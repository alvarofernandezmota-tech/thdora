# src/ai/intent_parser.py
"""
Intent parser for THDORA — v3 with regex + Groq tool calling.

Detects user intents from natural language and extracts entities.
Uses regex for simple intents (saves RPD), Groq FAST_MODEL for classification,
and Groq SMART_MODEL with tool calling for complex NLP.

Intents:
- nueva_cita: Create appointment
- borrar_cita: Delete appointment
- editar_cita: Update appointment
- log_habito: Log habit
- borrar_habito: Delete habit
- consulta_nlp: Complex NLP query (uses tool calling)
- desconocido: Unknown intent
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.ai.groq_client import get_groq_client, FAST_MODEL, SMART_MODEL

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result of intent parsing."""
    intent: str
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    model_used: str = ""
    from_cache: bool = False


INTENTS = {
    "nueva_cita": {"model": FAST_MODEL, "needs_groq": False},
    "borrar_cita": {"model": FAST_MODEL, "needs_groq": False},
    "editar_cita": {"model": FAST_MODEL, "needs_groq": False},
    "log_habito": {"model": FAST_MODEL, "needs_groq": False},
    "borrar_habito": {"model": FAST_MODEL, "needs_groq": False},
    "consulta_nlp": {"model": SMART_MODEL, "needs_groq": True},
    "desconocido": {"model": None, "needs_groq": False},
}

_TIME_PATTERN = re.compile(r"(\d{1,2}:\d{2})")
_DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")
_TODAY_PATTERN = re.compile(r"(hoy|today|ahora|now)", re.IGNORECASE)
_TOMORROW_PATTERN = re.compile(r"(mañana|tomorrow|manana)", re.IGNORECASE)
_YESTERDAY_PATTERN = re.compile(r"(ayer|yesterday)", re.IGNORECASE)


def _get_today() -> str:
    return date.today().isoformat()


def _get_tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def _get_yesterday() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def _extract_time(text: str) -> Optional[str]:
    match = _TIME_PATTERN.search(text)
    return match.group(1) if match else None


def _extract_date(text: str) -> str:
    match = _DATE_PATTERN.search(text)
    if match:
        return match.group(1)
    if _TODAY_PATTERN.search(text):
        return _get_today()
    if _TOMORROW_PATTERN.search(text):
        return _get_tomorrow()
    if _YESTERDAY_PATTERN.search(text):
        return _get_yesterday()
    return _get_today()


def _extract_name(text: str) -> str:
    text_lower = text.lower()
    for word in ["cita", "reunión", "reunion", "consulta", "dentista", "médico", "medico"]:
        if word in text_lower:
            parts = text_lower.split(word)
            if parts[1:]:
                name_part = parts[1].strip()
                if name_part:
                    return name_part.split()[0].title() if name_part.split() else "Cita"
    words = [w for w in text.split() if len(w) > 3 and (w[0].isupper() or w.isalpha())]
    return words[0] if words else "Cita"


def _extract_type(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["médica", "medica", "médico", "medico", "doctor", "dentista"]):
        return "médica"
    if any(w in text_lower for w in ["personal", "familia", "amigos"]):
        return "personal"
    if any(w in text_lower for w in ["trabajo", "reunión", "reunion", "oficina"]):
        return "trabajo"
    return "otra"


def _extract_value(text: str, units: List[str]) -> str:
    for unit in units:
        if unit in text:
            parts = text.split()
            for part in parts:
                if unit in part and part.replace(unit, "").replace(".", "").isdigit():
                    return part
    numbers = [w for w in text.split() if w.replace(".", "").isdigit()]
    return numbers[0] if numbers else ""


def _extract_habit_and_value(text: str) -> Tuple[str, str]:
    text_lower = text.lower()
    if any(w in text_lower for w in ["dorm", "sueño", "sleep"]):
        value = _extract_value(text_lower, ["horas", "h", "hora"])
        return "sueño", value or "8h"
    if any(w in text_lower for w in ["agua", "water", "beb", "beber"]):
        value = _extract_value(text_lower, ["vasos", "litros", "l", "ml", "botella"])
        return "agua", value or "2L"
    if any(w in text_lower for w in ["ejercicio", "gym", "deporte", "caminar", "correr"]):
        value = _extract_value(text_lower, ["minutos", "min", "horas", "h"])
        return "ejercicio", value or "30min"
    words = text.split()
    if len(words) >= 2:
        return words[0].lower(), " ".join(words[1:])
    return "", ""


def _extract_notes(text: str) -> str:
    return text


async def parse_intent(text: str, user_id: Optional[int] = None) -> IntentResult:
    """
    Parse user text and extract intent with entities.

    Uses regex for simple intents (saves RPD), then Groq for classification.

    Args:
        text: User input text
        user_id: Optional user ID for logging

    Returns:
        IntentResult with intent, confidence, entities, model_used
    """
    text_lower = text.lower().strip()

    if not text_lower:
        return IntentResult(intent="desconocido", confidence=0.0, model_used="regex")

    intent_result = _try_regex_intent(text, text_lower)
    if intent_result.intent != "desconocido":
        intent_result.from_cache = False
        intent_result.model_used = "regex"
        return intent_result

    try:
        groq_result = await _classify_with_groq(text, user_id)
        if groq_result.intent != "desconocido":
            return groq_result
    except Exception as e:
        logger.warning(f"Groq classification failed: {e}, falling back to regex")

    return IntentResult(intent="desconocido", confidence=0.0, model_used="fallback", from_cache=False)


def _try_regex_intent(text: str, text_lower: str) -> IntentResult:
    if any(w in text_lower for w in ["nueva cita", "nueva reunion", "nueva consulta", "añade cita", "agrega cita", "crear cita"]):
        time = _extract_time(text)
        dt = _extract_date(text)
        name = _extract_name(text)
        apt_type = _extract_type(text)
        notes = _extract_notes(text)
        entities = {"date": dt, "time": time or "09:00", "name": name, "type": apt_type, "notes": notes}
        return IntentResult(intent="nueva_cita", confidence=0.95, entities=entities)

    if any(w in text_lower for w in ["borra cita", "elimina cita", "cancela cita", "quitar cita", "borrar cita"]):
        dt = _extract_date(text)
        name = _extract_name(text)
        return IntentResult(intent="borrar_cita", confidence=0.90, entities={"date": dt, "name": name})

    if any(w in text_lower for w in ["mueve cita", "cambia cita", "edita cita", "modifica cita", "actualiza cita"]):
        dt = _extract_date(text)
        time = _extract_time(text)
        name = _extract_name(text)
        return IntentResult(intent="editar_cita", confidence=0.85, entities={"date": dt, "time": time, "name": name})

    if any(w in text_lower for w in ["dorm", "sueño", "agua", "ejercicio", "gym", "comí", "comi", "beb", "hice"]):
        habit, value = _extract_habit_and_value(text)
        dt = _extract_date(text)
        if habit:
            return IntentResult(intent="log_habito", confidence=0.90, entities={"date": dt, "habit": habit, "value": value})

    if any(w in text_lower for w in ["borra hábito", "elimina hábito", "borrar hábito"]):
        habit = _extract_name(text)
        dt = _extract_date(text)
        return IntentResult(intent="borrar_habito", confidence=0.85, entities={"date": dt, "habit": habit})

    if any(w in text_lower for w in ["qué", "cuando", "cuanto", "cuánta", "dime", "muestra", "resumen"]):
        return IntentResult(intent="consulta_nlp", confidence=0.70)

    return IntentResult(intent="desconocido", confidence=0.0)


async def _classify_with_groq(text: str, user_id: Optional[int] = None) -> IntentResult:
    client = get_groq_client()
    prompt = f"""Clasifica el siguiente texto en una de estas intenciones:
- nueva_cita
- borrar_cita
- editar_cita
- log_habito
- borrar_habito
- consulta_nlp
- desconocido

Texto: {text}

Responde SOLO con el nombre de la intención, nada más."""

    try:
        response = await client.ask(prompt, temperature=0.0, max_tokens=50)
        intent = response.strip().lower()
        if intent in INTENTS:
            return IntentResult(intent=intent, confidence=0.80, model_used=FAST_MODEL, from_cache=False)
    except Exception:
        pass

    return IntentResult(intent="desconocido", confidence=0.0, model_used=FAST_MODEL)
