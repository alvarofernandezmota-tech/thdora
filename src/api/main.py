"""
Entrypoint de la API REST de THDORA — v0.12.1
"""

from fastapi import FastAPI

from src.api.routers import appointments, habits, summary
from src.api.routers import habit_config
from src.api.routers import user_config
from src.api.routers import admin
from src.monitoring.health import router as health_router
from src.monitoring.middleware import MonitoringMiddleware
from src.monitoring.metrics import setup_prometheus

app = FastAPI(
    title="THDORA API",
    description="API REST del ecosistema de gestión personal THDORA",
    version="0.12.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware de métricas (latencia + logs HTTP) ──────────────────────────────────
app.add_middleware(MonitoringMiddleware)

# ── Routers de negocio ──────────────────────────────────────────────────────────────
app.include_router(appointments.router)
app.include_router(habits.router)
app.include_router(summary.router)
app.include_router(habit_config.router)
app.include_router(user_config.router)
app.include_router(admin.router)

# ── Monitoring ────────────────────────────────────────────────────────────────────
# /health/live  — liveness probe (Docker healthcheck)
# /health/ready — readiness probe (BD + agente)
app.include_router(health_router)

# /metrics — scraping Prometheus
setup_prometheus(app)


@app.get("/", tags=["health"])
def root() -> dict:
    """Raíz — healthcheck rápido para Docker y el entrypoint del bot."""
    return {"status": "ok", "service": "thdora", "version": "0.12.1"}
