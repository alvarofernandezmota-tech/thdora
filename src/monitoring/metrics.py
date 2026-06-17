"""
Métricas Prometheus personalizadas para THDORA.

Métricas expuestas:
    thdora_messages_total          — mensajes procesados por tipo
    thdora_agent_invocations_total — invocaciones LangGraph (ok/error)
    thdora_agent_response_seconds  — histograma de latencia del agente
    thdora_api_response_seconds    — histograma de latencia FastAPI
    thdora_active_users            — gauge de usuarios activos 24h
    thdora_build_info              — versión y modelo del sistema

Uso desde el agente:
    from src.monitoring.metrics import messages_total, agent_response_time
    messages_total.labels(user_id=str(uid), message_type="nlp").inc()
    with agent_response_time.time():
        result = await graph.ainvoke(...)
"""
from __future__ import annotations
import logging
from prometheus_client import Counter, Gauge, Histogram, Info

logger = logging.getLogger(__name__)

# —— Contadores ——
messages_total = Counter(
    "thdora_messages_total",
    "Total de mensajes procesados por el bot",
    ["user_id", "message_type"],
)
agent_invocations = Counter(
    "thdora_agent_invocations_total",
    "Número de invocaciones del agente LangGraph",
    ["success"],
)

# —— Histogramas ——
agent_response_time = Histogram(
    "thdora_agent_response_seconds",
    "Latencia del agente LangGraph (segundos)",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)
api_response_time = Histogram(
    "thdora_api_response_seconds",
    "Latencia de endpoints FastAPI (segundos)",
)

# —— Gauges ——
active_users = Gauge("thdora_active_users", "Usuarios activos en las últimas 24 horas")
long_term_memory_size = Gauge(
    "thdora_long_term_memory_chars",
    "Tamaño de la memoria larga por usuario (caracteres)",
    ["user_id"],
)

# —— Info estática ——
thdora_info = Info("thdora_build", "Versión y configuración del sistema")
thdora_info.info({"version": "0.21.1", "agent": "LangGraph", "llm": "Groq-Llama3.3"})


def setup_prometheus(app) -> None:
    """
    Expone /metrics con prometheus_client nativo (sin prometheus-fastapi-instrumentator).
    Evita el bug '_IncludedRouter has no attribute path' con FastAPI + sub-routers.

    Args:
        app: Instancia FastAPI.
    """
    from src.monitoring.config import monitoring_config
    if not monitoring_config.enable_prometheus:
        logger.warning("⚠️ Prometheus deshabilitado (MONITORING_ENABLE_PROMETHEUS=false)")
        return

    from fastapi import Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    @app.get(monitoring_config.metrics_endpoint, include_in_schema=False)
    def metrics() -> Response:
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    logger.info("✅ Prometheus configurado → %s", monitoring_config.metrics_endpoint)
