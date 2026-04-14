"""
Orquestador de lenguaje natural con Groq.

Flujo:
    1. llama-3.1-8b-instant  → clasifica el intent del mensaje
    2. llama-3.3-70b-versatile → extrae entidades JSON o responde en chat

Intents soportados:
    - nueva_cita    → crear cita en la API
    - log_habito    → registrar hábito en la API
    - consulta      → responder con info de citas/hábitos del día
    - chat          → respuesta conversacional libre
    - desconocido   → pedir aclaración al usuario

Memoria:
    Los últimos MAX_HISTORY mensajes se guardan en context.user_data["nlp_history"]
    y se envían a Groq para mantener contexto conversacional.
    Con PicklePersistence activo en main.py, este historial sobrevive
    reinicios del proceso bot.

Personalidad de THDORA (_CHAT_SYSTEM):
    Edita _CHAT_SYSTEM para cambiar tono, estilo o instrucciones de respuesta.
    El cambio tiene efecto inmediato sin reiniciar ningún otro módulo.

Variables de entorno:
    GROQ_API_KEY   → obligatoria
"""

import json
import logging
import os
import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from groq import AsyncGroq

logger = logging.getLogger(__name__)

# Cliente lazy — se inicializa la primera vez que se usa, no al importar.
# Esto garantiza que load_dotenv() ya haya ejecutado antes de leer la key.
_CLIENT: Optional[AsyncGroq] = None

def _get_client() -> Optional[AsyncGroq]:
    global _CLIENT
    if _CLIENT is None:
        key = os.getenv("GROQ_API_KEY", "")
        if key:
            _CLIENT = AsyncGroq(api_key=key)
    return _CLIENT


MODEL_FAST   = "llama-3.1-8b-instant"       # clasificador
MODEL_STRONG = "llama-3.3-70b-versatile"    # extracción + chat
MAX_HISTORY  = 10                            # mensajes de contexto

# Tipos de cita válidos en la API (con y sin tilde → normalización)
_TIPO_MAP = {
    "medica": "médica", "médica": "médica",
    "personal": "personal",
    "trabajo": "trabajo",
    "otro": "otro", "otra": "otro",
}
_TIPO_DEFAULT = "otro"


# ── Paso 1: Clasificador de intents ──────────────────────────────────

_CLASSIFY_SYSTEM = """
Clasifica el siguiente mensaje en UNO de estos intents. Responde SOLO con el nombre del intent:

- nueva_cita   → el usuario quiere crear/añadir una cita, evento, consulta o recordatorio con fecha/hora
- log_habito   → el usuario quiere registrar un hábito (dormir, agua, ejercicio, peso, etc.)
- consulta     → el usuario pregunta por sus citas o hábitos ya guardados
- chat         → conversación general, saludos, preguntas no relacionadas con agenda
- desconocido  → no se puede clasificar con certeza

Responde únicamente con una de las cinco palabras anteriores, sin puntuación ni explicación.
"""


async def classify_intent(text: str) -> str:
    client = _get_client()
    if not client:
        return "desconocido"
    try:
        resp = await client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {"role": "system", "content": _CLASSIFY_SYSTEM},
                {"role": "user",   "content": text},
            ],
            max_tokens=10,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip().lower()
        # Normalizar por si devuelve algo con puntuación
        for intent in ("nueva_cita", "log_habito", "consulta", "chat", "desconocido"):
            if intent in raw:
                return intent
        return "desconocido"
    except Exception as e:
        logger.error("Error clasificando intent: %s", e)
        return "desconocido"


# ── Paso 2a: Extracción de entidades para nueva_cita ─────────────────

def _build_cita_system(today: str) -> str:
    return f"""Hoy es {today}.
Extrae del mensaje del usuario los datos de la cita y devuelve JSON válido.
Campos obligatorios: name (str), date (YYYY-MM-DD), time (HH:MM), type (medica/personal/trabajo/otro).
Campos opcionales: notes (str, puede ser vacío).
Si no se menciona la fecha asume hoy ({today}). Si no se menciona la hora devuelve "09:00".
Devuelve ÚNICAMENTE el JSON, sin texto adicional, sin markdown, sin bloques de código.
Ejemplo de salida válida: {{"name":"Dentista","date":"{today}","time":"17:00","type":"medica","notes":""}}
"""


async def extract_cita(text: str, today: str) -> Optional[Dict]:
    client = _get_client()
    if not client:
        return None
    try:
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=[
                {"role": "system", "content": _build_cita_system(today)},
                {"role": "user",   "content": text},
            ],
            max_tokens=200,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        # Limpiar bloques markdown si Groq los incluye
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\n?```$", "", raw)
        # Extraer primer objeto JSON si hay texto extra
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            logger.warning("extract_cita: no JSON encontrado en: %r", raw)
            return None
        data = json.loads(m.group())
        # Normalizar tipo
        tipo_raw = str(data.get("type", "")).lower().strip()
        data["type"] = _TIPO_MAP.get(tipo_raw, _TIPO_DEFAULT)
        return data
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("extract_cita JSON error: %s — raw: %r", e, raw if 'raw' in dir() else '')
        return None
    except Exception as e:
        logger.error("extract_cita error inesperado: %s", e)
        return None


# ── Paso 2b: Extracción de entidades para log_habito ─────────────────

def _build_habito_system(today: str) -> str:
    return f"""Hoy es {today}.
Extrae del mensaje del usuario los datos del hábito y devuelve JSON válido.
Campos obligatorios: habit (nombre del hábito, str), value (valor registrado, str), date (YYYY-MM-DD).
Si no se menciona la fecha asume hoy ({today}).
Devuelve ÚNICAMENTE el JSON, sin texto adicional, sin markdown, sin bloques de código.
Ejemplo de salida válida: {{"habit":"sueño","value":"7 horas","date":"{today}"}}
"""


async def extract_habito(text: str, today: str) -> Optional[Dict]:
    client = _get_client()
    if not client:
        return None
    try:
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=[
                {"role": "system", "content": _build_habito_system(today)},
                {"role": "user",   "content": text},
            ],
            max_tokens=150,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\n?```$", "", raw)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            logger.warning("extract_habito: no JSON encontrado en: %r", raw)
            return None
        return json.loads(m.group())
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("extract_habito JSON error: %s", e)
        return None
    except Exception as e:
        logger.error("extract_habito error inesperado: %s", e)
        return None


# ── Paso 2c: Respuesta conversacional (chat / consulta / desconocido) ──

_CHAT_SYSTEM = """
Eres THDORA, asistente personal de Álvaro. Hablas en español, de forma directa y cercana.
Respondes en máximo 2 frases. Sin florituras ni saludos innecesarios.
Ayudas con agenda, hábitos y bienestar personal.
Cuando el usuario quiera crear una cita dile exactamente: "Escríbeme algo como: mañana dentista a las 5"
Cuando quiera registrar un hábito dile: "Escríbeme algo como: dormí 7 horas"
Nunca inventes datos de citas o hábitos que no te hayan dicho en esta conversación.
"""


async def chat_response(text: str, history: List[Dict[str, str]]) -> str:
    client = _get_client()
    if not client:
        return "⚠️ El asistente IA no está configurado. Verifica GROQ_API_KEY."
    try:
        messages = [
            {"role": "system", "content": _CHAT_SYSTEM},
            *history[-MAX_HISTORY:],
            {"role": "user", "content": text},
        ]
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=messages,
            max_tokens=200,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Error en chat_response: %s", e)
        return "⚠️ Error al conectar con el asistente. Inténtalo de nuevo."


# ── Orquestador principal ─────────────────────────────────────────────

async def route(
    text: str,
    user_data: dict,
) -> Dict[str, Any]:
    """
    Punto de entrada principal del router NLP.

    Devuelve un dict con:
        intent (str) — intent clasificado
        data   (dict | None) — entidades extraídas si aplica
        reply  (str | None)  — respuesta para el usuario si no hay data
    """
    today = date.today().isoformat()

    # Historial de conversación (para mantener contexto en chat)
    history: List[Dict[str, str]] = user_data.setdefault("nlp_history", [])

    intent = await classify_intent(text)
    logger.debug("Intent clasificado: %s — texto: %r", intent, text)

    # Añadir mensaje del usuario al historial
    history.append({"role": "user", "content": text})
    if len(history) > MAX_HISTORY * 2:
        history[:] = history[-(MAX_HISTORY * 2):]

    data  = None
    reply = None

    if intent == "nueva_cita":
        data = await extract_cita(text, today)
        if not data:
            reply = "No pude extraer los datos de la cita. Prueba: \"mañana dentista a las 5\""

    elif intent == "log_habito":
        data = await extract_habito(text, today)
        if not data:
            reply = "No pude extraer el hábito. Prueba: \"dormí 7 horas\""

    elif intent in ("consulta", "chat", "desconocido"):
        reply = await chat_response(text, history[:-1])  # sin el último que acabamos de añadir

    # Añadir respuesta del bot al historial
    if reply:
        history.append({"role": "assistant", "content": reply})

    return {"intent": intent, "data": data, "reply": reply}
