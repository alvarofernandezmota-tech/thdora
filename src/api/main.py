"""
Entrypoint de la API REST de THDORA.

Usa FastAPI para exponer el LifeManager como servicio HTTP.
Los endpoints completos se implementan en la Fase 6 del ROADMAP.

Ejecución::

    uvicorn src.api.main:app --reload
    # Swagger UI: http://localhost:8000/docs
    # ReDoc:      http://localhost:8000/redoc
"""

from fastapi import FastAPI
from src.core.impl.memory_lifemanager import MemoryLifeManager

app = FastAPI(
    title="THDORA API",
    description="API REST del ecosistema de gestión personal THDORA",
    version="0.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Instancia del gestor (en Fase 6 se inyectará mediante dependency injection)
_manager = MemoryLifeManager()


@app.get("/", tags=["health"])
def health_check() -> dict:
    """
    Health check del servicio.

    Returns:
        dict: Estado del servicio y versión.
    """
    return {"status": "ok", "service": "thdora", "version": "0.4.0"}


# TODO Fase 6: implementar endpoints completos
# @app.get("/appointments/{date}")
# @app.post("/appointments")
# @app.delete("/appointments/{apt_id}")
# @app.get("/habits/{date}")
# @app.post("/habits")
# @app.get("/summary/{date}")
