# ──────────────────────────────────────────────────────────────────
# THDORA — Dockerfile multi-stage
# Stage 1: builder (instala deps en /install)
# Stage 2: runtime (imagen final mínima, usuario no-root)
#
# El servicio a arrancar se controla via env var SERVICE_TARGET:
#   SERVICE_TARGET=api  → alembic + uvicorn
#   SERVICE_TARGET=bot  → python -m src.bot.main
# Configurar en docker-compose.yml:
#   environment:
#     SERVICE_TARGET: api
# ──────────────────────────────────────────────────────────────────

# ─ Stage 1: builder ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# ─ Stage 2: runtime ──────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas del builder
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY . .

# Copiar y preparar entrypoint ANTES de cambiar a usuario no-root
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Usuario no-root por seguridad
RUN useradd -m -u 1000 thdora && \
    mkdir -p /app/data /app/logs && \
    chown -R thdora:thdora /app /app/data /app/logs
USER thdora

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    SERVICE_TARGET=api

# Healthcheck — solo válido para el servicio API
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

ENTRYPOINT ["/entrypoint.sh"]
