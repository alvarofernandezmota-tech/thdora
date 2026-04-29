"""
Orquestador de lenguaje natural con Groq — modo Toki.

Flujo:
    1. llama-3.1-8b-instant  → clasifica el intent del mensaje
    2. llama-3.3-70b-versatile → extrae entidades JSON o responde en chat

Intents soportados:
    - nueva_cita      → crear cita en la API
    - borrar_cita     → borrar cita existente (resuelve por nombre/hora → id real)
    - editar_cita     → editar hora/nombre/tipo de cita existente
    - log_habito      → registrar hábito en la API
    - borrar_habito   → borrar registro de hábito del día
    - consulta        → responder con info de citas/hábitos del día (CONTEXTO REAL)
    - consulta_semana → responder con citas de los próximos 7 días
    - chat            → respuesta conversacional libre
    - desconocido     → el handler muestra el menú del bot (no responde texto solo)

Contexto real (modo Toki):
    route() acepta api_context: dict con citas y hábitos reales del día.
    chat_response() inyecta ese contexto en el system prompt para que el
    modelo responda con datos reales.

Desambiguación:
    extract_borrar_cita y extract_editar_cita ahora reciben TODAS las citas
    de la semana (no solo las de hoy). Si el modelo encuentra más de una
    candidata, devuelve {"candidates": [...]} en vez de un solo resultado.
    nlp.py detecta eso y muestra botones inline para que el usuario elija.

Cache TTL:
    route() admite un api_context ya cacheado desde nlp.py. El cacheo real
    vive en nlp.py para no mezclar responsabilidades.

Memoria:
    Los últimos MAX_HISTORY mensajes se guardan en context.user_data["nlp_history"]
    con PicklePersistence activo en main.py.

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

_CLIENT: Optional[AsyncGroq] = None


def _get_client() -> Optional[AsyncGroq]:
    """Devuelve (o crea) el cliente AsyncGroq singleton.

    Lazy-init: el cliente se crea la primera vez que se llama, siempre
    que GROQ_API_KEY esté definida en el entorno.
    Si la variable no existe devuelve None; todas las funciones públicas
    comprueban este caso y responden con mensajes de error sin llamar a la API.

    Returns:
        Instancia AsyncGroq lista para usar, o None si la clave no está configurada.
    """
    global _CLIENT
    if _CLIENT is None:
        key = os.getenv("GROQ_API_KEY", "")
        if key:
            _CLIENT = AsyncGroq(api_key=key)
    return _CLIENT


# ── Constantes de modelo y comportamiento ────────────────────────────────────

MODEL_FAST   = "llama-3.1-8b-instant"     # Clasificación rápida de intent
MODEL_STRONG = "llama-3.3-70b-versatile"  # Extracción de entidades y chat
MAX_HISTORY  = 10                          # Mensajes por dirección en user_data

# Normalización del campo 'type' de cita — el modelo puede devolver variantes
_TIPO_MAP = {
    "medica": "médica", "médica": "médica",
    "personal": "personal",
    "trabajo": "trabajo",
    "otro": "otra", "otra": "otra", "other": "otra",
}
_TIPO_DEFAULT = "otra"


# ── Paso 1: Clasificador de intents ──────────────────────────────────────────

_CLASSIFY_SYSTEM = """
Clasifica el siguiente mensaje en UNO de estos intents. Responde SOLO con el nombre del intent:

- nueva_cita      → el usuario quiere crear/añadir una cita, evento, consulta o recordatorio con fecha/hora
- borrar_cita     → el usuario quiere cancelar, eliminar o borrar una cita existente
- editar_cita     → el usuario quiere cambiar, mover, modificar o editar una cita existente
- log_habito      → el usuario quiere registrar un hábito (dormir, agua, ejercicio, peso, etc.)
- borrar_habito   → el usuario quiere eliminar o quitar un registro de hábito del día
- consulta        → el usuario pregunta por sus citas o hábitos de hoy o mañana
- consulta_semana → el usuario pregunta por su semana, varios días, o los próximos días
- chat            → conversación general, saludos, preguntas no relacionadas con agenda
- desconocido     → no se puede clasificar con certeza

Responde únicamente con una de las nueve palabras anteriores, sin puntuación ni explicación.
"""


async def classify_intent(text: str) -> str:
    """Clasifica el mensaje del usuario en uno de los 9 intents posibles.

    Usa MODEL_FAST (llama-3.1-8b-instant) para minimizar latencia.
    Temperatura 0.0 para máxima determinismo.

    Args:
        text: Mensaje en lenguaje natural del usuario.

    Returns:
        Intent como string: 'nueva_cita', 'borrar_cita', 'editar_cita',
        'log_habito', 'borrar_habito', 'consulta', 'consulta_semana',
        'chat' o 'desconocido'.
        Devuelve 'desconocido' si la API no está disponible o falla.
    """
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
        for intent in (
            "nueva_cita", "borrar_cita", "editar_cita",
            "log_habito", "borrar_habito",
            "consulta_semana", "consulta",
            "chat", "desconocido",
        ):
            if intent in raw:
                return intent
        return "desconocido"
    except Exception as e:
        logger.error("Error clasificando intent: %s", e)
        return "desconocido"


# ── Paso 2a: Extracción nueva_cita ──────────────────────────────────────────

def _build_cita_system(today: str) -> str:
    """Construye el system prompt para extraer datos de una cita nueva.

    Inyecta la fecha de hoy para que el modelo pueda inferir fechas relativas
    ('mañana', 'el lunes', etc.).

    Args:
        today: Fecha actual en formato YYYY-MM-DD.

    Returns:
        String con el system prompt listo para enviar a MODEL_STRONG.
    """
    return f"""Hoy es {today}.
Extrae del mensaje del usuario los datos de la cita y devuelve JSON válido.
Campos obligatorios: name (str), date (YYYY-MM-DD), time (HH:MM), type (médica/personal/trabajo/otra).
Campos opcionales: notes (str, puede ser vacío).
Si no se menciona la fecha asume hoy ({today}). Si no se menciona la hora devuelve "09:00".
Devuelve ÚNCIAMENTE el JSON, sin texto adicional, sin markdown, sin bloques de código.
Ejemplo de salida válida: {{"name":"Dentista","date":"{today}","time":"17:00","type":"médica","notes":""}}
"""


async def extract_cita(text: str, today: str) -> Optional[Dict]:
    """Extrae los campos de una cita nueva desde lenguaje natural.

    Llama a MODEL_STRONG con temperatura 0.0 para obtener un JSON con los
    campos obligatorios (name, date, time, type) y opcionales (notes).
    Normaliza el campo 'type' mediante _TIPO_MAP para garantizar valores válidos.

    Args:
        text:  Mensaje del usuario describiendo la cita.
        today: Fecha actual YYYY-MM-DD usada para resolver referencias relativas.

    Returns:
        Dict con las claves name/date/time/type/notes, o None si falla la
        extracción o el JSON del modelo es inválido.
    """
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
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\n?```$", "", raw)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            logger.warning("extract_cita: no JSON encontrado en: %r", raw)
            return None
        data = json.loads(m.group())
        tipo_raw = str(data.get("type", "")).lower().strip()
        data["type"] = _TIPO_MAP.get(tipo_raw, _TIPO_DEFAULT)
        return data
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("extract_cita JSON error: %s", e)
        return None
    except Exception as e:
        logger.error("extract_cita error inesperado: %s", e)
        return None


# ── Paso 2b: Extracción log_habito ──────────────────────────────────────────

def _build_habito_system(today: str) -> str:
    """Construye el system prompt para extraer datos de un registro de hábito.

    Args:
        today: Fecha actual en formato YYYY-MM-DD.

    Returns:
        String con el system prompt listo para enviar a MODEL_STRONG.
    """
    return f"""Hoy es {today}.
Extrae del mensaje del usuario los datos del hábito y devuelve JSON válido.
Campos obligatorios: habit (nombre del hábito, str), value (valor registrado, str), date (YYYY-MM-DD).
Si no se menciona la fecha asume hoy ({today}).
Devuelve ÚNCIAMENTE el JSON, sin texto adicional, sin markdown, sin bloques de código.
Ejemplo de salida válida: {{"habit":"sueño","value":"7 horas","date":"{today}"}}
"""


async def extract_habito(text: str, today: str) -> Optional[Dict]:
    """Extrae nombre, valor y fecha de un registro de hábito desde lenguaje natural.

    Args:
        text:  Mensaje del usuario describiendo el hábito registrado.
        today: Fecha actual YYYY-MM-DD.

    Returns:
        Dict con habit/value/date, o None si el modelo no devuelve JSON válido.
    """
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
            return None
        return json.loads(m.group())
    except Exception as e:
        logger.error("extract_habito error: %s", e)
        return None


# ── Paso 2c: Extracción borrar_cita ─────────────────────────────────────────
# Recibe TODAS las citas de la semana. Devuelve un único match o {"candidates": [...]}

def _build_borrar_cita_system(today: str, todas_citas: List[Dict]) -> str:
    """Construye el system prompt para identificar la cita a borrar.

    Lista TODAS las citas disponibles en el prompt para que el modelo
    identifique la correcta por nombre, hora o día mencionado.
    Si hay ambigüedad, el modelo devuelve 'candidates' en lugar de un solo ID.

    Args:
        today:       Fecha actual YYYY-MM-DD.
        todas_citas: Lista plana de citas (hoy + mañana + semana) generada
                     por build_todas_citas().

    Returns:
        System prompt con la lista de citas formateada para MODEL_STRONG.
    """
    citas_str = "\n".join(
        f"  id={c.get('id','?')} date={c.get('date', today)} index={c.get('index','?')}: {c.get('time','?')} — {c.get('name','?')}"
        for c in todas_citas
    ) or "  (ninguna)"
    return f"""Hoy es {today}.
El usuario quiere borrar una cita. Lista COMPLETA de citas de los próximos días:
{citas_str}

REGLAS:
1. Si identificas UNA sola cita con certeza, devuelve:
   {{"date": "YYYY-MM-DD", "id": <ID entero>, "index": <índice entero>, "name": "<nombre>"}}
2. Si hay VARIAS citas que coinciden (mismo nombre en distintos días u horas), devuelve:
   {{"candidates": [{{"date": "YYYY-MM-DD", "id": <int>, "index": <int>, "name": "<str>", "time": "HH:MM"}}, ...]}}
3. Si no puedes identificar ninguna con certeza devuelve:
   {{"date": "{today}", "id": -1, "index": -1, "name": ""}}
Si no se menciona fecha, busca en TODAS las fechas.
Devuelve ÚNCIAMENTE el JSON, sin texto adicional, sin markdown.
"""


async def extract_borrar_cita(
    text: str, today: str, todas_citas: List[Dict]
) -> Optional[Dict]:
    """Identifica la cita a borrar a partir del mensaje del usuario.

    Pasa la lista completa de citas al modelo para que resuelva por
    nombre, hora o día incluso si no se menciona el ID.

    Args:
        text:        Mensaje del usuario.
        today:       Fecha actual YYYY-MM-DD.
        todas_citas: Lista de todas las citas (de build_todas_citas).

    Returns:
        Dict con date/id/index/name si hay match único.
        Dict con 'candidates' si hay ambigüedad (el handler muestra botones).
        None si la API falla o el JSON es inválido.
    """
    client = _get_client()
    if not client:
        return None
    try:
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=[
                {"role": "system", "content": _build_borrar_cita_system(today, todas_citas)},
                {"role": "user",   "content": text},
            ],
            max_tokens=300,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\n?```$", "", raw)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return None
        return json.loads(m.group())
    except Exception as e:
        logger.error("extract_borrar_cita error: %s", e)
        return None


# ── Paso 2d: Extracción editar_cita ─────────────────────────────────────────
# Recibe TODAS las citas de la semana. Devuelve un único match o {"candidates": [...]}

def _build_editar_cita_system(today: str, todas_citas: List[Dict]) -> str:
    """Construye el system prompt para identificar la cita a editar y los cambios.

    Además de identificar la cita (id/index), el modelo extrae los campos
    new_time, new_name, new_type y new_notes de la petición del usuario.
    Si hay ambigüedad en la cita, devuelve 'candidates' más los cambios pedidos
    para aplicarlos después de que el usuario elija.

    Args:
        today:       Fecha actual YYYY-MM-DD.
        todas_citas: Lista plana de citas generada por build_todas_citas().

    Returns:
        System prompt listo para MODEL_STRONG.
    """
    citas_str = "\n".join(
        f"  id={c.get('id','?')} date={c.get('date', today)} index={c.get('index','?')}: {c.get('time','?')} — {c.get('name','?')}"
        for c in todas_citas
    ) or "  (ninguna)"
    return f"""Hoy es {today}.
El usuario quiere editar una cita. Lista COMPLETA de citas de los próximos días:
{citas_str}

REGLAS:
1. Si identificas UNA sola cita con certeza, devuelve:
   {{"date": "YYYY-MM-DD", "id": <int>, "index": <int>, "name": "<str>",
     "new_time": "HH:MM o null", "new_name": "str o null", "new_type": "str o null", "new_notes": "str o null"}}
2. Si hay VARIAS citas que coinciden, devuelve:
   {{"candidates": [{{"date": "YYYY-MM-DD", "id": <int>, "index": <int>, "name": "<str>", "time": "HH:MM"}}, ...],
     "new_time": "HH:MM o null", "new_name": "str o null", "new_type": "str o null", "new_notes": "str o null"}}
   (incluye los cambios pedidos junto a los candidatos para aplicarlos tras la elección)
3. Si no puedes identificar ninguna devuelve:
   {{"date": "{today}", "id": -1, "index": -1}}
Si no se menciona fecha, busca en TODAS las fechas.
Devuelve ÚNCIAMENTE el JSON, sin texto adicional, sin markdown.
"""


async def extract_editar_cita(
    text: str, today: str, todas_citas: List[Dict]
) -> Optional[Dict]:
    """Identifica la cita a editar y extrae los cambios solicitados.

    Devuelve tanto la cita identificada (id/index/date) como los campos
    a modificar (new_time, new_name, new_type, new_notes). Si hay ambigüedad
    en la identificación, devuelve 'candidates' junto a los cambios para
    que nlp.py los aplique tras la desambiguación del usuario.

    Args:
        text:        Mensaje del usuario.
        today:       Fecha actual YYYY-MM-DD.
        todas_citas: Lista de todas las citas (de build_todas_citas).

    Returns:
        Dict con id/index/date/new_* si hay match único.
        Dict con 'candidates' + new_* si hay ambigüedad.
        None si la API falla.
    """
    client = _get_client()
    if not client:
        return None
    try:
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=[
                {"role": "system", "content": _build_editar_cita_system(today, todas_citas)},
                {"role": "user",   "content": text},
            ],
            max_tokens=400,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\n?```$", "", raw)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return None
        return json.loads(m.group())
    except Exception as e:
        logger.error("extract_editar_cita error: %s", e)
        return None


# ── Paso 2e: Extracción borrar_habito ───────────────────────────────────────

def _build_borrar_habito_system(today: str, habitos_hoy: Dict) -> str:
    """Construye el system prompt para identificar el hábito a borrar.

    Lista los hábitos registrados hoy para que el modelo seleccione
    el nombre exacto (necesario para que la API lo localice).

    Args:
        today:       Fecha actual YYYY-MM-DD.
        habitos_hoy: Dict {nombre_habito: valor_registrado} del día.

    Returns:
        System prompt listo para MODEL_STRONG.
    """
    habs_str = "\n".join(
        f"  • {k}: {v}" for k, v in habitos_hoy.items()
    ) or "  (ninguno registrado)"
    return f"""Hoy es {today}.
El usuario quiere borrar un hábito registrado. Hábitos de hoy:
{habs_str}

Identifica cuál hábito quiere borrar y devuelve JSON:
{{"date": "YYYY-MM-DD", "habit": "<nombre exacto del hábito>"}}
Si no se menciona fecha asume hoy ({today}).
Si no puedes identificar el hábito devuelve: {{"date": "{today}", "habit": ""}}
Devuelve ÚNCIAMENTE el JSON, sin texto adicional, sin markdown.
"""


async def extract_borrar_habito(
    text: str, today: str, habitos_hoy: Dict
) -> Optional[Dict]:
    """Identifica el hábito a borrar por nombre desde lenguaje natural.

    Args:
        text:        Mensaje del usuario.
        today:       Fecha actual YYYY-MM-DD.
        habitos_hoy: Hábitos registrados hoy {nombre: valor}.

    Returns:
        Dict con date/habit (nombre exacto), o None si la API falla.
        habit puede ser '' si el modelo no identifica el hábito —
        route() detecta ese caso y responde con mensaje de error.
    """
    client = _get_client()
    if not client:
        return None
    try:
        resp = await client.chat.completions.create(
            model=MODEL_STRONG,
            messages=[
                {"role": "system", "content": _build_borrar_habito_system(today, habitos_hoy)},
                {"role": "user",   "content": text},
            ],
            max_tokens=100,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\n?```$", "", raw)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return None
        return json.loads(m.group())
    except Exception as e:
        logger.error("extract_borrar_habito error: %s", e)
        return None


# ── Paso 2f: Respuesta contextual (chat / consulta) ──────────────────────────

_CHAT_SYSTEM_BASE = """
Eres THDORA, la asistente personal de Álvaro. Tu objetivo es ayudarle a gestionar
su vida diaria con claridad, proactividad y un toque cercano.

Personalidad:
- Directa y concisa: máximo 2-3 frases por respuesta, sin florituras.
- Cercana pero profesional: tratas a Álvaro por su nombre cuando encaja.
- Proactiva: si detectas que algo en su agenda puede ser relevante, lo mencionas.
- Sin inventar: NUNCA improvises datos de citas o hábitos que no estén en el contexto.
- En español siempre.

Cuando el usuario quiera crear una cita dile exactamente: "Escíbeme algo como: mañana dentista a las 5"
Cuando quiera registrar un hábito dile: "Escíbeme algo como: dormí 7 horas"
Cuando quiera borrar una cita dile: "Escíbeme algo como: cancela el dentista de hoy"
Cuando quiera editar una cita dile: "Escíbeme algo como: mueve el gym a las 18"
"""


def _build_chat_system(
    api_context: Optional[Dict],
    username: Optional[str] = None,
) -> str:
    """Construye el system prompt completo para chat_response inyectando contexto real.

    Parte de _CHAT_SYSTEM_BASE y añade un bloque CONTEXTO ACTUAL con las
    citas y hábitos reales del día desde la API. Si api_context es None
    devuelve solo el system base (el modelo responderá sin datos concretos).

    Args:
        api_context: Dict con claves 'citas', 'habitos', 'citas_manana',
                     'citas_semana', 'semana_raw'. Puede ser None.
        username:    Nombre del usuario Telegram para personalizar el saludo.
                     Si se provee, reemplaza 'Álvaro' en el system prompt.

    Returns:
        String con el system prompt completo listo para MODEL_STRONG.
    """
    base = _CHAT_SYSTEM_BASE
    if username:
        base = base.replace("Álvaro", username)

    if not api_context:
        return base

    citas        = api_context.get("citas", [])
    habitos      = api_context.get("habitos", {})
    manana_citas = api_context.get("citas_manana", [])
    semana_citas = api_context.get("citas_semana", "")

    ctx_lines = []

    if citas:
        citas_str = ", ".join(
            f"{c.get('time','?')} {c.get('name','?')}" for c in citas
        )
        ctx_lines.append(f"Citas de hoy: {citas_str}")
    else:
        ctx_lines.append("Citas de hoy: ninguna")

    if manana_citas:
        manana_str = ", ".join(
            f"{c.get('time','?')} {c.get('name','?')}" for c in manana_citas
        )
        ctx_lines.append(f"Citas de mañana: {manana_str}")

    if semana_citas:
        ctx_lines.append(f"Citas próximos días:\n{semana_citas}")

    if habitos:
        habs_str = ", ".join(f"{k}: {v}" for k, v in habitos.items())
        ctx_lines.append(f"Hábitos de hoy: {habs_str}")
    else:
        ctx_lines.append("Hábitos de hoy: ninguno registrado")

    context_block = "\n".join(ctx_lines)
    return f"{base}\n\nCONTEXTO ACTUAL:\n{context_block}"


async def chat_response(
    text: str,
    history: List[Dict[str, str]],
    api_context: Optional[Dict] = None,
    username: Optional[str] = None,
) -> str:
    """Genera una respuesta conversacional con contexto real de la agenda.

    Usa MODEL_STRONG con temperatura 0.7 (más creativo que la extracción)
    e inyecta el historial de conversación (hasta MAX_HISTORY mensajes)
    para mantener coherencia entre turnos.

    También sirve a los intents 'consulta' y 'consulta_semana' cuando
    la respuesta es texto libre (no extracción de entidades).

    Args:
        text:        Mensaje actual del usuario.
        history:    Lista de dicts {role, content} con el historial previo.
                    Se trunca a MAX_HISTORY entradas automáticamente.
        api_context: Contexto real de citas y hábitos (opcional).
        username:   Nombre Telegram para personalizar la respuesta.

    Returns:
        Respuesta en texto para el usuario. Si la API no está disponible
        devuelve un mensaje de error descriptivo.
    """
    client = _get_client()
    if not client:
        return "⚠️ El asistente IA no está configurado. Verifica GROQ_API_KEY."
    try:
        system = _build_chat_system(api_context, username=username)
        messages = [
            {"role": "system", "content": system},
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


# ── Helpers ————————————————————————————————————————————————————————————————

def build_todas_citas(api_context: Dict) -> List[Dict]:
    """Construye una lista plana de TODAS las citas disponibles en api_context.

    Combina citas de hoy, mañana y el resto de la semana (semana_raw) en una
    única lista, añadiendo el campo 'date' a cada cita si no lo tiene.
    Deduplica por 'id' para evitar repeticiones cuando hoy/mañana ya
    aparecen en semana_raw.

    Usada por extract_borrar_cita y extract_editar_cita para pasar al modelo
    TODAS las citas posibles y habilitar la desambiguación multi-día.

    Args:
        api_context: Dict devuelto por la API con claves 'citas', 'citas_manana'
                     y 'semana_raw' (date_str → [citas]).

    Returns:
        Lista de dicts de citas, cada uno con el campo 'date' garantizado.
        Sin duplicados por id.
    """
    today    = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    resultado: List[Dict] = []

    for c in api_context.get("citas", []):
        resultado.append({**c, "date": c.get("date", today)})

    for c in api_context.get("citas_manana", []):
        resultado.append({**c, "date": c.get("date", tomorrow)})

    # semana_raw contiene el dict date_str → [citas] completo
    for day_str, day_citas in api_context.get("semana_raw", {}).items():
        if day_str in (today, tomorrow):
            continue
        for c in day_citas:
            resultado.append({**c, "date": day_str})

    # Dedup por id para no repetir si hoy/mañana ya están en semana_raw
    seen: set = set()
    dedup = []
    for c in resultado:
        cid = c.get("id")
        if cid is not None and cid not in seen:
            seen.add(cid)
            dedup.append(c)
        elif cid is None:
            dedup.append(c)
    return dedup


# ── Orquestador principal ————————————————————————————————————————————

async def route(
    text: str,
    user_data: dict,
    api_context: Optional[Dict] = None,
    username: Optional[str] = None,
) -> Dict[str, Any]:
    """Punto de entrada principal del router NLP.

    Orquesta el flujo completo de dos pasos:
    1. classify_intent — determina qué quiere hacer el usuario
    2. extract_* / chat_response — extrae entidades o genera respuesta

    Gestiona también el historial de conversación en user_data y la
    resolución de ambigüedad devolviendo 'candidates' cuando hay varias
    citas candidatas para borrar/editar.

    Args:
        text:        Mensaje del usuario.
        user_data:   context.user_data de PTB donde se persiste 'nlp_history'.
        api_context: Datos reales de la API inyectados desde nlp.py (con cache TTL).
                     Estructura: {citas, habitos, citas_manana, citas_semana,
                     semana_raw}.
        username:    Nombre Telegram del usuario para personalizar respuestas.

    Returns:
        Dict con:
            intent         (str)        — intent clasificado
            data           (dict|None)  — entidades extraídas si aplica
            candidates     (list|None)  — lista de citas candidatas si ambigüedad
            reply          (str|None)   — respuesta para el usuario
            show_menu      (bool)       — True si el handler debe mostrar el menú
            pending_action (str|None)   — 'borrar_cita' o 'editar_cita' si candidates
            pending_changes(dict|None)  — cambios new_* pendientes de aplicar (editar)
    """
    today    = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    history: List[Dict[str, str]] = user_data.setdefault("nlp_history", [])

    intent = await classify_intent(text)
    logger.debug("Intent clasificado: %s — texto: %r", intent, text)

    history.append({"role": "user", "content": text})
    if len(history) > MAX_HISTORY * 2:
        history[:] = history[-(MAX_HISTORY * 2):]

    data            = None
    candidates      = None
    reply           = None
    show_menu       = False
    pending_action  = None
    pending_changes = None

    todas_citas = build_todas_citas(api_context or {})
    habitos_hoy = (api_context or {}).get("habitos", {})

    # ── nueva_cita ────────────────────────────────────────────────────
    if intent == "nueva_cita":
        data = await extract_cita(text, today)
        if not data:
            reply = "No pude extraer los datos de la cita. Prueba: \"mañana dentista a las 5\""

    # ── borrar_cita ───────────────────────────────────────────────────
    elif intent == "borrar_cita":
        result = await extract_borrar_cita(text, today, todas_citas)
        if result and "candidates" in result:
            candidates     = result["candidates"]
            pending_action = "borrar_cita"
        elif result and result.get("id", -1) != -1:
            data = result
        else:
            reply = (
                "No encontré la cita que quieres borrar. "
                "Prueba: \"cancela el dentista de hoy\" o usa /citas para verlas."
            )

    # ── editar_cita ───────────────────────────────────────────────────
    elif intent == "editar_cita":
        result = await extract_editar_cita(text, today, todas_citas)
        if result and "candidates" in result:
            candidates      = result["candidates"]
            pending_action  = "editar_cita"
            pending_changes = {
                k: result.get(k)
                for k in ("new_time", "new_name", "new_type", "new_notes")
            }
        elif result and result.get("id", -1) != -1:
            data = result
        else:
            reply = (
                "No encontré la cita que quieres editar. "
                "Prueba: \"mueve el gym de hoy a las 18\" o usa /citas para verlas."
            )

    # ── log_habito ────────────────────────────────────────────────────
    elif intent == "log_habito":
        data = await extract_habito(text, today)
        if not data:
            reply = "No pude extraer el hábito. Prueba: \"dormí 7 horas\""

    # ── borrar_habito ─────────────────────────────────────────────────
    elif intent == "borrar_habito":
        data = await extract_borrar_habito(text, today, habitos_hoy)
        if not data or not data.get("habit"):
            reply = (
                "No encontré el hábito que quieres borrar. "
                "Prueba: \"quita el registro de agua de hoy\" o usa /habitos para verlos."
            )
            data = None

    # ── consulta ──────────────────────────────────────────────────────
    elif intent == "consulta":
        # Detecta si la consulta es sobre mañana para ajustar el contexto
        ctx = api_context or {}
        if any(w in text.lower() for w in ("mañana", "manana", "tomorrow")):
            ctx = {**ctx, "fecha_consulta": tomorrow}
        reply = await chat_response(text, history[:-1], api_context=ctx, username=username)

    # ── consulta_semana ───────────────────────────────────────────────
    elif intent == "consulta_semana":
        reply = await chat_response(text, history[:-1], api_context=api_context, username=username)

    # ── chat ──────────────────────────────────────────────────────────
    elif intent == "chat":
        reply = await chat_response(text, history[:-1], api_context=api_context, username=username)

    # ── desconocido ───────────────────────────────────────────────────
    elif intent == "desconocido":
        # El handler nlp.py mostrará el menú principal del bot
        show_menu = True
        reply = None

    if reply:
        history.append({"role": "assistant", "content": reply})

    return {
        "intent":          intent,
        "data":            data,
        "candidates":      candidates,
        "reply":           reply,
        "show_menu":       show_menu,
        "pending_action":  pending_action,
        "pending_changes": pending_changes,
    }
