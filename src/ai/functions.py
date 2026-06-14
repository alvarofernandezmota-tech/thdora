"""
Schemas de function calling para Groq — THDORA NLP.

Uso:
    from src.ai.functions import GROQ_FUNCTIONS
    # Pasar a la llamada de Groq:
    # client.chat.completions.create(..., tools=GROQ_FUNCTIONS, tool_choice="auto")
"""

GROQ_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": (
                "Crea una nueva cita en la agenda del usuario. "
                "Úsala cuando el usuario quiera añadir un evento, consulta, "
                "reunión o cualquier actividad con fecha y hora concretas."
            ),
            "parameters": {
                "type": "object",
                "required": ["title", "date", "time"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Nombre o descripción de la cita. Ej: 'Dentista', 'Reunión con Ana'.",
                    },
                    "date": {
                        "type": "string",
                        "description": "Fecha de la cita en formato YYYY-MM-DD. Ej: '2026-06-16'.",
                    },
                    "time": {
                        "type": "string",
                        "description": "Hora de inicio en formato HH:MM (24h). Ej: '17:00'.",
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duración en minutos. Por defecto 60 si no se especifica.",
                        "default": 60,
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notas adicionales opcionales sobre la cita.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_habit_done",
            "description": (
                "Registra un hábito completado por el usuario. "
                "Úsala cuando el usuario indique que ha realizado una actividad "
                "habitual: dormir, beber agua, hacer ejercicio, tomar medicación, etc."
            ),
            "parameters": {
                "type": "object",
                "required": ["habit_name", "value", "date"],
                "properties": {
                    "habit_name": {
                        "type": "string",
                        "description": (
                            "Nombre del hábito tal como lo conoce el sistema. "
                            "Ej: 'sueño', 'agua', 'ejercicio', 'peso'."
                        ),
                    },
                    "value": {
                        "type": "string",
                        "description": (
                            "Valor registrado para el hábito. "
                            "Ej: '7 horas', '2L', '45 minutos', '75 kg'."
                        ),
                    },
                    "date": {
                        "type": "string",
                        "description": "Fecha del registro en formato YYYY-MM-DD. Ej: '2026-06-15'.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
]
