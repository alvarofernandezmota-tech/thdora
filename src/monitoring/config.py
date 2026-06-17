"""
Configuración del módulo de monitoreo.
Variables de entorno con prefijo MONITORING_ (p.ej. MONITORING_ENABLE_PROMETHEUS=false).
"""
from __future__ import annotations
from pydantic_settings import BaseSettings


class MonitoringConfig(BaseSettings):
    enable_prometheus: bool = True
    metrics_endpoint: str = "/metrics"
    log_level: str = "INFO"

    model_config = {"env_prefix": "MONITORING_", "env_file": ".env", "extra": "ignore"}


monitoring_config = MonitoringConfig()
