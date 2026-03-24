"""
Implementaciones concretas de AbstractLifeManager.

Exporta:
    - MemoryLifeManager : implementación en memoria (desarrollo/testing)
    - JsonLifeManager   : persistencia JSON local (Fase 5)

Próximamente:
    - SqlLifeManager    : base de datos real (Fase 11)
"""

from src.core.impl.memory_lifemanager import MemoryLifeManager
from src.core.impl.json_lifemanager import JsonLifeManager

__all__ = ["MemoryLifeManager", "JsonLifeManager"]
