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
from src.api.routers import habit_config
from src.api.deps import get_manager
from src.core.impl.sqlite_lifemanager import SQLiteLifeManager

app = FastAPI(
    title="THDORA API",
    description="API REST del ecosistema de gestión personal THDORA",
    version="0.9.2",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(appointments.router)
app.include_router(habits.router)
app.include_router(summary.router)
app.include_router(habit_config.router)


@app.get("/", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "service": "thdora", "version": "0.9.2"}
