"""
Templates adicionales de prompts para tareas específicas.

Uso: resumen de conversación, desambiguación, etc.
"""
from __future__ import annotations

SUMMARY_PROMPT = """\
Eres un asistente que genera resúmenes de memoria para {user_name}.
Genera un resumen claro (máx. 400 palabras) que capture:
- Objetivos y prioridades del usuario
- Hábitos y rutinas mencionadas
- Información importante (preferencias, proyectos, etc.)
- Logros o eventos relevantes

Conversación reciente:
{conversation_text}

Resumen:\
"""

DISAMBIG_PROMPT = """\
El usuario ha dicho: "{user_message}"
No queda claro si se refiere a una cita o a un hábito.
Pregunta de forma natural y breve para aclarar.\
"""
