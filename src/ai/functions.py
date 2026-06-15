"""
Groq tool calling functions for THDORA.

Defines GROQ_FUNCTIONS schema used by GroqClient for tool calling.
Tools allow the LLM to query and modify appointments and habits.
"""

from typing import Any, Dict, List

GROQ_FUNCTIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_appointments",
            "description": "Obtener las citas de un día específico del usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Fecha en formato YYYY-MM-DD. Usa 'hoy' para la fecha actual."
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "Crear una nueva cita para el usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "time": {"type": "string", "description": "Hora HH:MM"},
                    "name": {"type": "string", "description": "Nombre o descripción de la cita"},
                    "type": {
                        "type": "string",
                        "enum": ["médica", "personal", "trabajo", "otra"],
                        "description": "Tipo de cita"
                    },
                    "notes": {"type": "string", "description": "Notas adicionales (opcional)"}
                },
                "required": ["date", "time", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_appointment",
            "description": "Eliminar una cita por fecha e índice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "index": {"type": "integer", "description": "Índice de la cita (0-based)"}
                },
                "required": ["date", "index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_habits",
            "description": "Obtener los hábitos registrados de un día.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Fecha YYYY-MM-DD"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_habit",
            "description": "Registrar un hábito del usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "habit": {"type": "string", "description": "Nombre del hábito (ej: sueño, agua, ejercicio)"},
                    "value": {"type": "string", "description": "Valor registrado (ej: 8h, 2L, 30min)"}
                },
                "required": ["date", "habit", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Obtener el resumen completo del día: citas y hábitos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Fecha YYYY-MM-DD"}
                },
                "required": ["date"]
            }
        }
    }
]
