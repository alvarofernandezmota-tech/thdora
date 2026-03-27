"""
Dependencias de la API — v2 con SQLiteLifeManager.

A partir de F9, la API usa SQLiteLifeManager por defecto.
El MemoryLifeManager queda como fallback para tests.

Uso en routers::

    from src.api.deps import get_manager

    @router.get("/appointments/{date}")
    def list_appointments(date: str, mgr = Depends(get_manager)):
        return mgr.get_appointments(date)
"""

from functools import lru_cache

from src.core.impl.sqlite_lifemanager import SQLiteLifeManager


@lru_cache(maxsize=1)
def get_manager() -> SQLiteLifeManager:
    """
    Singleton del manager de datos.
    lru_cache garantiza una sola instancia durante toda la vida del proceso.
    """
    return SQLiteLifeManager()
