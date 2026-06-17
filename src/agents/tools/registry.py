"""
Registro central de tools del agente THDORA.

Importa y agrupa todas las tools disponibles.
get_all_tools() es el único punto de entrada para el grafo.

Añadir nuevas tools:
    1. Crea el archivo en src/agents/tools/
    2. Importa la tool aquí y añádela a _ALL_TOOLS.
"""
from __future__ import annotations
from langchain_core.tools import BaseTool
from .appointments import crear_cita, consultar_citas, borrar_cita
from .habits import registrar_habito

_ALL_TOOLS: list[BaseTool] = [
    crear_cita,
    consultar_citas,
    borrar_cita,
    registrar_habito,
]


def get_all_tools() -> list[BaseTool]:
    """Devuelve la lista completa de tools registradas para el agente."""
    return _ALL_TOOLS
