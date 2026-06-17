"""
Health checks para Docker y orquestación.

Endpoints:
    GET /health/live   — liveness probe (el contenedor está vivo)
    GET /health/ready  — readiness probe (BD + agente disponibles)

Integración en src/api/main.py:
    from src.monitoring.health import router as health_router
    app.include_router(health_router)
"""
from __future__ import annotations
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Monitoring"])


@router.get("/live")
async def liveness():
    """Liveness probe — siempre 200 si el proceso está corriendo."""
    return {"status": "alive"}


@router.get("/ready")
async def readiness():
    """
    Readiness probe — verifica base de datos y que el grafo LangGraph compila.
    Devuelve 200 si todo está listo, 503 si algo falla.
    """
    checks: dict[str, str] = {}
    ok = True

    # BD
    try:
        from src.db.session import get_db
        with get_db() as db:
            db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        ok = False

    # Agente LangGraph
    try:
        from src.agents import build_thdora_graph
        build_thdora_graph()  # cacheado: no reconstruye si ya existe
        checks["agent"] = "ok"
    except Exception as exc:
        checks["agent"] = f"error: {exc}"
        ok = False

    from fastapi import Response
    status_code = 200 if ok else 503
    return Response(
        content=str({"status": "ready" if ok else "degraded", **checks}),
        status_code=status_code,
        media_type="application/json",
    )
