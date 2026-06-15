"""GroqRouter: NLP via Groq API con system prompt estructurado y few-shot examples."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ToolCallResult:
    action: str
    success: bool
    data: dict
    message_to_user: str


@dataclass
class AmbiguityRequest:
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
                    "tipo": {"type": "string", "description": "Categoría: médica, personal, trabajo, otro.", "enum": ["médica", "personal", "trabajo", "otro"]},
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


def build_system_prompt(nombre_usuario: str | None = None) -> str:
    """Construye el system prompt personalizado para el asistente Toki."""
    nombre = nombre_usuario or "Usuario"

    ejemplos_correctos = json.dumps(
        [
            {
                "usuario": "Pon una cita con el dentista el viernes a las 10",
                "respuesta": {
                    "intent": "crear_cita", "accion": "crear_cita",
                    "entidades": {"nombre": "Dentista", "fecha": "2025-06-20", "hora": "10:00", "tipo": "médica"},
                    "respuesta_usuario": "✅ Cita con el Dentista creada para el viernes 20 jun a las 10:00.",
                },
            },
            {
                "usuario": "Marca que hoy hice ejercicio",
                "respuesta": {
                    "intent": "registrar_habito", "accion": "registrar_habito",
                    "entidades": {"habito": "ejercicio", "fecha": "hoy"},
                    "respuesta_usuario": "💪 ¡Ejercicio registrado para hoy!",
                },
            },
            {
                "usuario": "¿Qué tengo esta semana?",
                "respuesta": {
                    "intent": "consultar_semana", "accion": "consultar_semana",
                    "entidades": {},
                    "respuesta_usuario": "📅 Aquí tienes tu semana...",
                },
            },
        ],
        ensure_ascii=False, indent=2,
    )

    ejemplos_rechazo = json.dumps(
        [
            {
                "usuario": "¿Cuál es la capital de Francia?",
                "respuesta": {
                    "intent": "fuera_de_scope", "accion": None, "entidades": {},
                    "respuesta_usuario": "Lo siento, solo puedo ayudarte con tu agenda y hábitos. ¿Quieres añadir una cita o registrar un hábito?",
                },
            },
            {
                "usuario": "Escríbeme un poema sobre el mar",
                "respuesta": {
                    "intent": "fuera_de_scope", "accion": None, "entidades": {},
                    "respuesta_usuario": "Eso está fuera de mis capacidades 😊. Estoy especializado en gestionar tu agenda y hábitos. ¿En qué puedo ayudarte con eso?",
                },
            },
        ],
        ensure_ascii=False, indent=2,
    )

    return f"""Eres Toki, asistente personal de {nombre}. Gestionas citas y hábitos.

## TU ROL
- Ayudas a {nombre} a gestionar su agenda (citas, recordatorios) y sus hábitos diarios.
- Interpretas lenguaje natural en español y extraes la intención y los datos relevantes.

## LÍMITES ESTRICTOS
- SOLO respondes sobre agenda, citas, recordatorios y hábitos.
- Si el usuario pregunta algo fuera de este scope, rechazas educadamente y rediriges.
- No das consejos médicos, legales, financieros ni de otro tipo.
- No generas contenido creativo, código ni información general.

## FORMATO DE RESPUESTA
Responde SIEMPRE con un objeto JSON válido con estos campos exactos:
{{
  "intent": "<crear_cita|borrar_cita|consultar_citas|consultar_semana|registrar_habito|fuera_de_scope|aclaracion>",
  "accion": "<nombre_de_la_accion o null>",
  "entidades": {{<campos extraídos del mensaje>}},
  "respuesta_usuario": "<mensaje en español para mostrar al usuario>"
}}

## EJEMPLOS DE USO CORRECTO
{ejemplos_correctos}

## EJEMPLOS DE RECHAZO EDUCADO
{ejemplos_rechazo}

## REGLAS ADICIONALES
- Las fechas relativas ("mañana", "el viernes", "la próxima semana") las resuelves con la hora actual del contexto.
- Si falta información obligatoria (fecha u hora para crear una cita), usa intent "aclaracion" y pregunta solo lo que falta.
- Responde siempre en español, con tono amigable y conciso.
- Nunca inventes datos que el usuario no haya proporcionado.
"""


class GroqRouter:
    """Enruta mensajes de texto a Groq y ejecuta las acciones resultantes."""

    def __init__(self) -> None:
        self._api_key: str = os.environ["GROQ_API_KEY"]
        self._model: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        self._base_url: str = "https://api.groq.com/openai/v1"

    async def process(
        self,
        user_text: str,
        user_id: int = 0,
        nombre_usuario: str | None = None,
        context_str: str = "",
        timeout: httpx.Timeout | None = None,
    ) -> str | ToolCallResult | AmbiguityRequest:
        """Procesa un mensaje de texto y retorna la respuesta o acción correspondiente."""
        _timeout = timeout or httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)
        system_prompt = build_system_prompt(nombre_usuario)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        if context_str:
            messages.append({"role": "system", "content": f"CONTEXTO ACTUAL DEL USUARIO:\n{context_str}"})
        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self._model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "max_tokens": 1024,
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=_timeout) as client:
            resp = await client.post(f"{self._base_url}/chat/completions", json=payload, headers=headers)
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

    async def _handle_tool_call(self, tool_call: dict, user_id: int) -> ToolCallResult | AmbiguityRequest:
        """Procesa un tool_call de Groq y ejecuta la acción correspondiente."""
        func_name = tool_call["function"]["name"]
        try:
            args = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError:
            args = {}

        if func_name == "crear_cita":
            missing = [f for f in ("fecha", "hora") if not args.get(f)]
            if missing:
                preguntas = {
                    "fecha": "¿Para qué fecha quieres la cita? (ej: mañana, el viernes)",
                    "hora": "¿A qué hora? (ej: 10:30, por la tarde)",
                }
                q = " ".join(preguntas[m] for m in missing)
                return AmbiguityRequest(intent="crear_cita", missing_fields=missing, question_to_user=q)
            return ToolCallResult(
                action="crear_cita", success=True, data=args,
                message_to_user=f"✅ Cita '{args.get('nombre')}' programada para {args.get('fecha')} a las {args.get('hora', 'hora pendiente')}.",
            )

        if func_name == "borrar_cita":
            cita_id = args.get("cita_id")
            return ToolCallResult(
                action="borrar_cita", success=True, data={"cita_id": cita_id},
                message_to_user=f"🗑️ Cita #{cita_id} eliminada correctamente.",
            )

        if func_name == "consultar_citas":
            return ToolCallResult(
                action="consultar_citas", success=True, data=args,
                message_to_user=f"📅 Consultando citas para {args.get('fecha')}...",
            )

        return ToolCallResult(
            action=func_name, success=False, data=args,
            message_to_user=f"No reconozco la acción '{func_name}'.",
        )
