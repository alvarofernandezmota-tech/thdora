import json
import logging
from datetime import datetime
from groq import Groq
from src.bot.api_client import ApiClient

logger = logging.getLogger(__name__)


class GroqRouter:
    def __init__(self):
        self.client = Groq()
        self.api_client = ApiClient()
        self.model = "llama-3.3-70b-versatile"

    # TAREA 1.2: System prompt rico Toki — anti-complacente, directo, honesto
    SYSTEM_PROMPT = """Eres Toki, un agente de bienestar emocional anti-complaciente, directo y honesto.
No eres un terapeuta ni das consejos médicos. Tu rol es ayudar al usuario a gestionar su vida diaria
(citas, hábitos, rutinas) y detectar patrones emocionales de forma útil aunque incomode.

LÍMITES ESTRICTOS:
- Nunca diagnostiques ni recetes tratamientos.
- Si el usuario parece necesitar ayuda profesional, recómiendala con respeto.
- No adules ni valides todo. Di la verdad aunque sea incómoda.
- No seas carca ni paternalista — sé cercano pero firme.

CAPACIDADES REALES:
- Crear, listar, editar y borrar citas.
- Registrar y hacer seguimiento de hábitos.
- Recordatorios y resumen diario.
- Detectar patrones en el estado emocional del usuario a lo largo del tiempo.

COMO RESPONDE TOKI (ejemplos):

Usuario: "Estoy muy estresado con el trabajo"
Toki: "Entiendo que sientes estrés. ¿Qué cita o hábito concreto te está generando más presión esta semana? Vamos a priorizar una cosa real en lugar de dar vueltas."

Usuario: "Tengo dentista el jueves a las 5"
Toki: "Perfecto. Creo la cita 'Dentista' el jueves a las 17:00. ¿Cuánto dura aproximadamente?"

Usuario: "Sí, hoy sí que voy al gimnasio"
Toki: "Lo mismo dijiste el lunes. Hoy tienes hueco a las 18:00. Si quieres que lo ponga como cita fija, dímelo."

COMO NO RESPONDE TOKI:
- "¡Qué bien! ¡Eres increíble!"
- "Entiendo perfectamente cómo te sientes, eso es muy difícil..."
- Respuestas largas sin acción concreta.

Responde siempre en español. Tono natural, cercano, sin ser pelota."""

    # Definicion de tools para function calling
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "create_appointment",
                "description": "Crea una nueva cita en el calendario del usuario",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "titulo": {"type": "string", "description": "Título de la cita"},
                        "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                        "hora": {"type": "string", "description": "Hora en formato HH:MM"},
                        "duracion_min": {"type": "integer", "description": "Duración en minutos", "default": 60}
                    },
                    "required": ["titulo", "fecha", "hora"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_appointments",
                "description": "Lista las citas de una fecha concreta",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"}
                    },
                    "required": ["fecha"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_appointment",
                "description": "Borra una cita por su ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cita_id": {"type": "integer", "description": "ID de la cita a borrar"}
                    },
                    "required": ["cita_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "log_habit",
                "description": "Registra el cumplimiento de un hábito",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "habit_id": {"type": "integer"},
                        "fecha": {"type": "string", "description": "YYYY-MM-DD"},
                        "valor": {"type": "number", "description": "Valor o check (1 = cumplido)"}
                    },
                    "required": ["habit_id", "fecha"]
                }
            }
        }
    ]

    async def process_message(
        self,
        message: str,
        user_id: int,
        citas_hoy: list,
        habitos: list,
        history: list
    ) -> str:
        # TAREA 1.3: Contexto dinamico inyectado en cada llamada
        now = datetime.now()
        dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        context_str = f"""CONTEXTO ACTUAL:
Fecha y hora: {now.strftime('%Y-%m-%d %H:%M')} ({dias_es[now.weekday()]})
Citas de hoy: {json.dumps(citas_hoy, ensure_ascii=False) if citas_hoy else 'Ninguna'}
Hábitos activos: {json.dumps(habitos, ensure_ascii=False) if habitos else 'Ninguno'}
Historial reciente: {json.dumps(history, ensure_ascii=False) if history else 'Sin historial previo'}"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "system", "content": context_str},
            *history,
            {"role": "user", "content": message}
        ]

        # TAREA 1.4: Function calling real
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.TOOLS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=800
        )

        choice = response.choices[0]

        # Si el modelo quiere llamar una tool
        if choice.message.tool_calls:
            tool_call = choice.message.tool_calls[0]
            fn_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            logger.info(f"Tool call: {fn_name} args:{args} user:{user_id}")

            try:
                tool_result = await self._execute_tool(fn_name, args, user_id)
            except Exception as e:
                logger.error(f"Tool execution error: {fn_name} - {e}")
                tool_result = {"error": str(e)}

            # Segunda llamada al modelo con el resultado de la tool
            messages.append(choice.message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False)
            })

            final = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=400
            )
            return final.choices[0].message.content

        return choice.message.content

    async def _execute_tool(self, fn_name: str, args: dict, user_id: int) -> dict:
        """Ejecuta la tool llamada por el modelo."""
        if fn_name == "create_appointment":
            return self.api_client.create_appointment(
                user_id=user_id,
                titulo=args["titulo"],
                fecha=args["fecha"],
                hora=args["hora"],
                duracion_min=args.get("duracion_min", 60)
            )
        elif fn_name == "list_appointments":
            return self.api_client.get_appointments(user_id, args["fecha"])
        elif fn_name == "delete_appointment":
            return self.api_client.delete_appointment(args["cita_id"])
        elif fn_name == "log_habit":
            return self.api_client.log_habit(
                user_id=user_id,
                habit_id=args["habit_id"],
                fecha=args["fecha"],
                valor=args.get("valor", 1)
            )
        else:
            raise ValueError(f"Tool desconocida: {fn_name}")
