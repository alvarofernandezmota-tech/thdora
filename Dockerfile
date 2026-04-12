# ──────────────────────────────────────────────────────────────────────────
# THDORA — Dockerfile
# Imagen única usada tanto por el servicio `api` como por `bot`.
# El punto de entrada se elige en docker-compose.yml mediante `command`.
#
# Build:
#   docker build -t thdora .
#
# La imagen NO incluye:
#   • tests/ ni docs/ (excluidos en .dockerignore)
#   • data/ (montada como volumen externo)
#   • .env (pasado como env_file en docker-compose)
# ──────────────────────────────────────────────────────────────────────────

# ─ Stage 1: dependencias ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema necesarias para compilar (SQLite, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─ Stage 2: imagen final ───────────────────────────────────────────────────────────
FROM python:3.12-slim

# Usuario no-root para seguridad
RUN groupadd -r thdora && useradd -r -g thdora thdora

WORKDIR /app

# Copiar deps compiladas del stage builder
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY src/ ./src/
COPY pyproject.toml .

# Carpeta de datos (será montada como volumen — se crea para permisos)
RUN mkdir -p /app/data && chown -R thdora:thdora /app

# Copiar entrypoints
COPY docker/entrypoint-api.sh /entrypoint-api.sh
COPY docker/entrypoint-bot.sh /entrypoint-bot.sh
RUN chmod +x /entrypoint-api.sh /entrypoint-bot.sh

USER thdora

# Variables de entorno por defecto (sobreescribibles en docker-compose)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    THDORA_API_URL=http://api:8000 \
    THDORA_DB_PATH=/app/data/thdora.db

EXPOSE 8000
