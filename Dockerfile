# ──────────────────────────────────────────────────────────────────
# THDORA — Dockerfile multi-stage
# Stage 1: builder (instala deps)
# Stage 2: runtime (imagen final mínima)
# ──────────────────────────────────────────────────────────────────

# ─ Stage 1: builder ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependencias de sistema necesarias para compilar
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

# Runtime deps mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas del builder
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY . .

# Usuario no-root por seguridad
RUN useradd -m -u 1000 thdora && chown -R thdora:thdora /app
USER thdora

# Variables de entorno por defecto (sobreescribibles via .env / docker-compose)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Healthcheck para el servicio API (usado por docker-compose depends_on)
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# ──────────────────────────────────────────────────────────────────
# ENTRYPOINT diferenciado por TARGET (api o bot)
# Se selecciona en docker-compose.yml via variable CMD o command:
#   api:  alembic upgrade head && uvicorn ...
#   bot:  python -m src.bot.main
# ──────────────────────────────────────────────────────────────────
ARG SERVICE_TARGET=api
ENV SERVICE_TARGET=${SERVICE_TARGET}

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
