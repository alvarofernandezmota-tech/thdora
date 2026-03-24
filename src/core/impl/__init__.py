"""
Implementaciones concretas de AbstractLifeManager.

Exporta:
    - MemoryLifeManager : implementación en memoria (desarrollo/testing)

Próximamente:
    - JsonLifeManager   : persistencia JSON local (Fase 5)
    - ApiLifeManager    : sincronización REST (Fase 6)
"""

from src.core.impl.memory_lifemanager import MemoryLifeManager

__all__ = ["MemoryLifeManager"]
