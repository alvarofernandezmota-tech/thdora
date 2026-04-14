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

Variables de entorno:
    GROQ_API_KEY   → obligatoria
"""

import json
import logging
import os
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


# ── Utilidades de fecha ──────────────────────────────────────────────

def _today() -> str:
    return date.today().isoformat()

def _tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


# ── Historial de conversación ────────────────────────────────────────

def get_history(user_data: dict) -> List[Dict[str, str]]:
    return user_data.get("nlp_history", [])

def push_history(user_data: dict, role: str, content: str) -> None:
    history = user_data.setdefault("nlp_history", [])
    history.append({"role": role, "content": content})
    if len(history) > MAX_HISTORY * 2:
        user_data["nlp_history"] = history[-(MAX_HISTORY * 2):]


# ── Paso 1: Clasificar intent ─────────────────────────────────────────

_CLASSIFY_SYSTEM = """
Eres un clasificador de intenciones para un asistente personal en español.
Analizas el mensaje del usuario y devuelves SOLO una de estas palabras, sin más texto:

- nueva_cita    → quiere crear una cita, cita médica, reunión, evento, etc.
- log_habito    → quiere registrar un hábito (sueño, ejercicio, agua, etc.)
- consulta      → pregunta por sus citas o hábitos del día/semana
- chat          → pregunta general, conversación libre, pregunta de conocimiento
- desconocido   → no está claro qué quiere

Responde ÚNICAMENTE con una de esas palabras exactas.
"""

async def classify_intent(text: str) -> str:
    client = _get_client()
    if not client:
        logger.warning("GROQ_API_KEY no configurada — intent desconocido")
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
        intent = resp.choices[0].message.content.strip().lower()
        valid  = {"nueva_cita", "log_habito", "consulta", "chat", "desconocido"}
        return intent if intent in valid else "desconocido"
    except Exception as e:
        logger.error("Error clasificando intent: %s", e)
        return "desconocido"


# ── Paso 2a: Extraer entidades para nueva_cita ────────────────────────

async def extract_cita(text: str, history: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    client = _get_client()
    if not client:
        return None

    cita_system = f"""
Eres un extractor de datos para crear citas en un asistente personal.
Hoy es {_today()} y mañana es {_tomorrow()}.
Extraes los datos del mensaje y devuelves SOLO un JSON válido con este formato exacto:

{{"date": "YYYY-MM-DD", "time": "HH:MM", "name": "título", "type": "tipo", "notes": ""}}

Reglas:
- date: infiere la fecha. "mañana" = {_tomorrow()}, "hoy" = {_today()}, "el lunes" = próximo lunes, etc.
- time: formato 24h. "las 5" = "17:00", "las 5 de la tarde" = "17:00", "las 9" = "09:00".
- name: título breve de la cita (ej: "Dentista", "Reunión con Ana", "Médico").
- type: uno de: "medica", "personal", "trabajo", "otro".
- notes: notas adicionales o string vacío.

Devuelve SOLO el JSON, sin texto adicional.
"""
    try:
        messages = [
            {"role": "system", "content": cita_system},
            *history[-6:],
            {"role": "user", "content": text},
        ]
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=messages,
            max_tokens=150,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        return json.loads(raw)
    except Exception as e:
        logger.error("Error extrayendo cita: %s", e)
        return None


# ── Paso 2b: Extraer entidades para log_habito ────────────────────────

async def extract_habito(text: str, history: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    client = _get_client()
    if not client:
        return None

    habito_system = f"""
Eres un extractor de datos para registrar hábitos en un asistente personal.
Hoy es {_today()}.
Extraes los datos del mensaje y devuelves SOLO un JSON válido con este formato exacto:

{{"date": "YYYY-MM-DD", "habit": "nombre_habito", "value": "valor"}}

Reglas:
- date: "hoy" = {_today()}, "ayer" = la fecha de ayer, etc.
- habit: nombre del hábito tal como suele registrarlo (ej: "Sueño", "Ejercicio", "Agua", "Peso").
- value: el valor registrado como string (ej: "7h", "30min", "2L", "72kg", "sí").

Devuelve SOLO el JSON, sin texto adicional.
"""
    try:
        messages = [
            {"role": "system", "content": habito_system},
            *history[-6:],
            {"role": "user", "content": text},
        ]
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=messages,
            max_tokens=100,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        return json.loads(raw)
    except Exception as e:
        logger.error("Error extrayendo hábito: %s", e)
        return None


# ── Paso 2c: Respuesta conversacional (chat / consulta / desconocido) ──

_CHAT_SYSTEM = """
Eres THDORA, un asistente personal amigable y conciso en español.
Ayudas al usuario con su agenda, hábitos y bienestar.
Respondes de forma breve (máximo 3 frases), cálida y directa.
Si el usuario quiere crear una cita di: "Puedes decirme algo como: mañana dentista a las 5"
Si quiere registrar un hábito di: "Puedes decirme algo como: dormí 7 horas"
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
            max_tokens=300,
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
    Punto de entrada principal.

    Devuelve un dict con:
        {"intent": str, "data": dict|None, "reply": str|None}

    - intent: el intent clasificado
    - data:   entidades extraídas (para nueva_cita / log_habito)
    - reply:  texto listo para enviar al usuario (para chat/desconocido)
              o None si data contiene los datos para que el handler actúe
    """
    history = get_history(user_data)
    intent  = await classify_intent(text)
    push_history(user_data, "user", text)

    if intent == "nueva_cita":
        data = await extract_cita(text, history)
        if data:
            push_history(user_data, "assistant", f"[cita creada: {data}]")
            return {"intent": intent, "data": data, "reply": None}
        # Si falla la extracción, caemos a chat
        reply = await chat_response(text, history)
        push_history(user_data, "assistant", reply)
        return {"intent": "chat", "data": None, "reply": reply}

    if intent == "log_habito":
        data = await extract_habito(text, history)
        if data:
            push_history(user_data, "assistant", f"[hábito registrado: {data}]")
            return {"intent": intent, "data": data, "reply": None}
        reply = await chat_response(text, history)
        push_history(user_data, "assistant", reply)
        return {"intent": "chat", "data": None, "reply": reply}

    # chat / consulta / desconocido → respuesta conversacional
    reply = await chat_response(text, history)
    push_history(user_data, "assistant", reply)
    return {"intent": intent, "data": None, "reply": reply}
