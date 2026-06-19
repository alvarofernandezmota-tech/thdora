#!/bin/sh
# THDORA entrypoint — selecciona arranque según SERVICE_TARGET
# Usado por docker-compose: SERVICE_TARGET=api | bot
set -e

echo "🚀 Iniciando THDORA — TARGET: ${SERVICE_TARGET}"

if [ "${SERVICE_TARGET}" = "api" ]; then
    echo "🗃️ Ejecutando migraciones Alembic..."
    alembic upgrade head
    echo "✅ Migraciones aplicadas"
    echo "🌐 Arrancando FastAPI..."
    exec uvicorn src.api.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 1 \
        --log-level info
elif [ "${SERVICE_TARGET}" = "bot" ]; then
    echo "🤖 Arrancando bot Telegram..."
    exec python -m src.bot.main
else
    echo "❌ SERVICE_TARGET desconocido: ${SERVICE_TARGET}"
    exit 1
fi
