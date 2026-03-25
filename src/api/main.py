"""
Entrypoint de la API REST de THDORA.

Usa FastAPI para exponer el LifeManager como servicio HTTP.

Ejecución::

    uvicorn src.api.main:app --reload
    # Swagger UI: http://localhost:8000/docs
    # ReDoc:      http://localhost:8000/redoc
"""

from fastapi import FastAPI

from src.api.routers import appointments, habits, summary
from src.core.impl.json_lifemanager import JsonLifeManager

app = FastAPI(
    title="THDORA API",
    description="API REST del ecosistema de gestión personal THDORA",
    version="0.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

_manager = JsonLifeManager()


def get_manager() -> JsonLifeManager:
    """
    Dependency para inyectar el gestor en los endpoints.
    En tests se sobreescribe con app.dependency_overrides.
    """
    return _manager


app.dependency_overrides[JsonLifeManager] = get_manager

app.include_router(appointments.router)
app.include_router(habits.router)
app.include_router(summary.router)


@app.get("/", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "service": "thdora", "version": "0.6.0"}
