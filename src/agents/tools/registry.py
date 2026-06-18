"""
Registro central de tools del agente THDORA.

get_all_tools() es el único punto de entrada para el grafo.
Todos los imports son lazy para evitar que ThdoraApiClient()
se instancie al arrancar — solo se crea cuando el agente ejecuta una tool.

Añadir nuevas tools:
    1. Crea el archivo en src/agents/tools/
    2. Impórtala dentro de get_all_tools() y añádela a la lista.
"""
from __future__ import annotations
from langchain_core.tools import BaseTool


def get_all_tools() -> list[BaseTool]:
    """Devuelve la lista completa de tools registradas (lazy imports)."""
    from .appointments import crear_cita, consultar_citas, borrar_cita
    from .habits import registrar_habito
    return [
        crear_cita,
        consultar_citas,
        borrar_cita,
        registrar_habito,
    ]
