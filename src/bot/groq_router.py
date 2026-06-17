"""GroqRouter: NLP vía Groq API con system prompt estructurado, few-shot y function calling."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache

import httpx

from src.bot.http_client import get_client
from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ToolCallResult:
    """Resultado de una llamada a herramienta exitosa."""

    action: str
    success: bool
    data: dict
    message_to_user: str


@dataclass
class AmbiguityRequest:
    """Solicitud de aclaración cuando faltan campos obligatorios."""

    intent: str
    missing_fields: list[str]
    question_to_user: str


TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "crear_cita",
            "description": "Crea una nueva cita en la agenda del usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre o descripción de la cita."},
                    "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD."},
                    "hora": {"type": "string", "description": "Hora en formato HH:MM (24h)."},
                    "tipo": {
                        "type": "string",
                        "description": "Categoría: médica, personal, trabajo, otro.",
                        "enum": ["médica", "personal", "trabajo", "otro"],
                    },
                },
                "required": ["nombre", "fecha"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "borrar_cita",
            "description": "Elimina una cita existente por su ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cita_id": {"type": "integer", "description": "ID numérico de la cita a eliminar."},
                },
                "required": ["cita_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_citas",
            "description": "Consulta las citas de una fecha concreta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD."},
                },
                "required": ["fecha"],
            },
        },
    },
]

# Ejemplos compactos — sin indent=2 para ahorrar ~300 tokens por llamada
_EJEMPLOS_OK = json.dumps(
    [
        {
            "usuario": "Pon una cita con el dentista el viernes a las 10",
            "respuesta": {
                "intent": "crear_cita",
                "accion": "crear_cita",
                "entidades": {"nombre": "Dentista", "fecha": "2025-06-20", "hora": "10:00", "tipo": "médica"},
                "respuesta_usuario": "\u2705 Cita con el Dentista creada para el viernes 20 jun a las 10:00.",
            },
        },
        {
            "usuario": "Marca que hoy hice ejercicio",
            "respuesta": {
                "intent": "registrar_habito",
                "accion": "registrar_habito",
                "entidades": {"habito": "ejercicio", "fecha": "hoy"},
                "respuesta_usuario": "\ud83d\udcaa \u00a1Ejercicio registrado para hoy!",
            },
        },
    ],
    ensure_ascii=False,
)

_EJEMPLOS_RECHAZO = json.dumps(
    [
        {
            "usuario": "\u00bfCuál es la capital de Francia?",
            "respuesta": {
                "intent": "fuera_de_scope",
                "accion": None,
                "entidades": {},
                "respuesta_usuario": "Lo siento, solo puedo ayudarte con tu agenda y hábitos.",
            },
        },
    ],
    ensure_ascii=False,
)


@lru_cache(maxsize=32)
def build_system_prompt(nombre_usuario: str | None = None) -> str:
    """Construye el system prompt para Groq. Cacheado por nombre de usuario."""
    nombre = nombre_usuario or "Usuario"
    return f"""Eres Toki, asistente personal de {nombre}. Gestionas citas y hábitos.

## ROL
Ayudas a {nombre} con agenda y hábitos. Interpretas lenguaje natural en español.

## LÍMITES
- SOLO agenda, citas, recordatorios y hábitos.
- Sin consejos médicos, legales, financieros ni contenido creativo.

## RESPUESTA
Responde SIEMPRE con JSON válido:
{{"intent":"<crear_cita|borrar_cita|consultar_citas|consultar_semana|registrar_habito|fuera_de_scope|aclaracion>","accion":"<accion o null>","entidades":{{}},"respuesta_usuario":"<mensaje en español>"}}

## EJEMPLOS
{_EJEMPLOS_OK}

## RECHAZO
{_EJEMPLOS_RECHAZO}

## REGLAS
- Fechas relativas las resuelves con la hora del contexto.
- Si falta fecha/hora obligatoria: intent "aclaracion", pregunta solo lo que falta.
- Responde en español, tono amigable y conciso. No inventes datos.
"""


_GROQ_TIMEOUT = httpx.Timeout(connect=5.0, read=45.0, write=10.0, pool=5.0)


class GroqRouter:
    """Router NLP que usa Groq para clasificar intents y ejecutar function calling."""

    def __init__(self) -> None:
        self._api_key: str = settings.GROQ_API_KEY
        self._model: str = settings.GROQ_MODEL
        self._base_url: str = "https://api.groq.com/openai/v1"

    async def process(
        self,
        user_text: str,
        user_id: int = 0,
        nombre_usuario: str | None = None,
        context_str: str = "",
        timeout: httpx.Timeout | None = None,
    ) -> str | ToolCallResult | AmbiguityRequest:
        """Procesa un mensaje de texto libre y devuelve una respuesta o una acción."""
        _timeout = timeout or _GROQ_TIMEOUT
        system_prompt = build_system_prompt(nombre_usuario)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        if context_str:
            messages.append({"role": "system", "content": f"CONTEXTO:\n{context_str}"})
        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self._model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "max_tokens": 256,
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        resp = await get_client().post(
            f"{self._base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=_timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        message = choice["message"]

        if message.get("tool_calls"):
            return await self._handle_tool_call(message["tool_calls"][0], user_id)

        content = message.get("content", "")
        try:
            parsed = json.loads(content)
            return parsed.get("respuesta_usuario", content)
        except (json.JSONDecodeError, AttributeError):
            return content

    async def _handle_tool_call(
        self, tool_call: dict, user_id: int
    ) -> ToolCallResult | AmbiguityRequest:
        """Procesa el resultado de un tool_call de Groq y devuelve la acción correspondiente."""
        func_name = tool_call["function"]["name"]
        try:
            args = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError:
            args = {}

        if func_name == "crear_cita":
            missing = [f for f in ("fecha", "hora") if not args.get(f)]
            if missing:
                preguntas = {
                    "fecha": "\u00bfPara qué fecha quieres la cita? (ej: mañana, el viernes)",
                    "hora": "\u00bfA qué hora? (ej: 10:30, por la tarde)",
                }
                return AmbiguityRequest(
                    intent="crear_cita",
                    missing_fields=missing,
                    question_to_user=" ".join(preguntas[m] for m in missing),
                )
            return ToolCallResult(
                action="crear_cita",
                success=True,
                data=args,
                message_to_user=f"\u2705 Cita '{args.get('nombre')}' programada para {args.get('fecha')} a las {args.get('hora', 'hora pendiente')}.",
            )

        if func_name == "borrar_cita":
            return ToolCallResult(
                action="borrar_cita",
                success=True,
                data={"cita_id": args.get("cita_id")},
                message_to_user=f"\ud83d\uddd1\ufe0f Cita #{args.get('cita_id')} eliminada correctamente.",
            )

        if func_name == "consultar_citas":
            return ToolCallResult(
                action="consultar_citas",
                success=True,
                data=args,
                message_to_user=f"\ud83d\udcc5 Consultando citas para {args.get('fecha')}...",
            )

        return ToolCallResult(
            action=func_name,
            success=False,
            data=args,
            message_to_user=f"No reconozco la acción '{func_name}'.",
        )

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio usando Groq Whisper large-v3. Para el handler de voz (Sprint 3)."""
        files = {"file": ("audio.ogg", audio_bytes, "audio/ogg")}
        data = {"model": "whisper-large-v3", "language": "es"}
        r = await get_client().post(
            f"{self._base_url}/audio/transcriptions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            files=files,
            data=data,
        )
        r.raise_for_status()
        return r.json()["text"]
