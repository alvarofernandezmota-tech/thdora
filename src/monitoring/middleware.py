"""
Middleware de monitoreo para FastAPI.

Registra latencia de cada request en el histograma api_response_time
y emite un log estructurado con método, path, status y duración.

Integración en src/api/main.py:
    from src.monitoring.middleware import MonitoringMiddleware
    app.add_middleware(MonitoringMiddleware)
"""
from __future__ import annotations
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.monitoring.metrics import api_response_time

logger = logging.getLogger("thdora.http")


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware que mide latencia y registra cada request HTTP."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        api_response_time.observe(elapsed)
        logger.info(
            "%s %s → %s (%.0fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed * 1000,
        )
        return response
