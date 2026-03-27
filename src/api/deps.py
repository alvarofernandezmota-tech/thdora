"""
Dependencias compartidas de la API THDORA.

Proporciona un singleton de ``JsonLifeManager`` para que todos los
routers compartan la misma instancia y el mismo fichero JSON.

Uso en routers::

    from fastapi import Depends
    from src.api.deps import get_manager

    @router.get("/...")
    def mi_endpoint(manager = Depends(get_manager)):
        ...

Por qué singleton:
    JsonLifeManager mantiene una caché en memoria (_data) que se
    sincroniza con el fichero JSON en cada escritura. Si cada request
    creara una instancia nueva, las escrituras concurrentes podrían
    sobreescribirse entre sí. Con un singleton compartido, todas las
    operaciones pasan por el mismo objeto y el fichero siempre refleja
    el estado real.
¿Cuándo migrar?
    En Fase 11 (SQLAlchemy) este módulo se reemplaza por una sesión
    de base de datos. El resto del código no cambia.
"""

from functools import lru_cache

from src.core.impl.json_lifemanager import JsonLifeManager


@lru_cache(maxsize=1)
def get_manager() -> JsonLifeManager:
    """
    Devuelve el singleton de JsonLifeManager.

    ``lru_cache(maxsize=1)`` garantiza que solo se crea una instancia
    durante toda la vida del proceso, independientemente de cuántos
    requests lleguen en paralelo.

    Returns:
        La única instancia de JsonLifeManager del proceso.
    """
    return JsonLifeManager()
