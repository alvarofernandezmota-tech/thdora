"""
Entrypoint de la API REST de THDORA.

Usa FastAPI para exponer el LifeManager como servicio HTTP.

Ejecución::

    uvicorn src.api.main:app --reload
    # Swagger UI: http://localhost:8000/docs
    # ReDoc:      http://localhost:8000/redoc
"""

from fastapi import FastAPI

from src.api.routers import appointments, habits
from src.core.impl.json_lifemanager import JsonLifeManager

app = FastAPI(
    title="THDORA API",
    description="API REST del ecosistema de gestión personal THDORA",
    version="0.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Instancia compartida del gestor (inyectada en los routers vía Depends)
_manager = JsonLifeManager()


def get_manager() -> JsonLifeManager:
    """
    Dependency para inyectar el gestor en los endpoints.

    Devuelve siempre la misma instancia (singleton de proceso).
    En tests, se sobreescribe con app.dependency_overrides.

    Returns:
        JsonLifeManager: Instancia del gestor con persistencia JSON.
    """
    return _manager


# Override de Depends en routers con la instancia real
app.dependency_overrides[JsonLifeManager] = get_manager

# Registrar routers
app.include_router(appointments.router)
app.include_router(habits.router)


@app.get("/", tags=["health"])
def health_check() -> dict:
    """
    Health check del servicio.

    Returns:
        dict: Estado del servicio y versión.
    """
    return {"status": "ok", "service": "thdora", "version": "0.5.0"}
