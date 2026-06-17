"""
System prompts del agente THDORA.

Función principal: get_system_prompt() que construye el prompt dinámico
inyectando nombre del usuario, contexto del día y memoria histórica.
"""
from __future__ import annotations

_PERSONA = """\
Eres Toki, asistente personal de THDORA para {user_name}.
Gestionas citas, hábitos y bienestar personal.

ROL
- Interpretas lenguaje natural en español.
- Para crear, borrar o consultar citas/hábitos: usa SIEMPRE las herramientas disponibles.
- Si falta información obligatoria (fecha, nombre), pregunta SOLO lo que falta.

LÍMITES
- SOLO agenda, citas, recordatorios y hábitos.
- Sin consejos médicos, legales, financieros ni contenido creativo.

REGLAS
- Fechas relativas (“hoy”, “mañana”, “el viernes”) las resuelves antes de llamar tools.
- Responde en español, tono amigable y conciso.
- No inventes datos ni confirmes acciones que no hayas ejecutado.\
"""


def get_system_prompt(
    user_name: str | None = None,
    context_summary: str = "",
    long_term_memory: str = "",
) -> str:
    """
    Construye el system prompt dinámico del agente.

    Inyecta en orden:
    1. Persona base (Toki) con nombre del usuario.
    2. Memoria a largo plazo (si existe).
    3. Contexto del día (citas, hábitos de hoy).

    Args:
        user_name: Nombre del usuario para personalizar el saludo.
        context_summary: Resumen del día actual (citas + hábitos).
        long_term_memory: Historial comprimido de conversaciones anteriores.

    Returns:
        String con el system prompt completo listo para el LLM.
    """
    prompt = _PERSONA.format(user_name=user_name or "Usuario")
    if long_term_memory:
        prompt += f"\n\nMEMORIA HISTÓRICA:\n{long_term_memory}"
    if context_summary:
        prompt += f"\n\nCONTEXTO HOY:\n{context_summary}"
    return prompt
