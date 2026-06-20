#!/bin/sh
# ============================================================
# THDORA — Entrypoint unificado
# Selecciona el servicio a arrancar via SERVICE_TARGET env var:
#   SERVICE_TARGET=api  → alembic stamp heads && alembic upgrade heads + uvicorn
#   SERVICE_TARGET=bot  → python -m src.bot.main
# Uso en docker-compose:
#   environment:
#     SERVICE_TARGET: api   # o bot
# ============================================================
set -e

# Crear directorios necesarios si no existen
mkdir -p /app/data /app/logs

echo "[entrypoint] SERVICE_TARGET=${SERVICE_TARGET:-api}"

case "${SERVICE_TARGET:-api}" in

  api)
    echo "[entrypoint] Ejecutando migraciones Alembic..."
    alembic stamp heads && alembic upgrade heads
    echo "[entrypoint] Migraciones OK. Arrancando API (uvicorn)..."
    exec uvicorn src.api.main:app \
      --host 0.0.0.0 \
      --port 8000 \
      --workers 1 \
      --log-level info \
      --access-log
    ;;

  bot)
    echo "[entrypoint] Arrancando Bot (Telegram PTB)..."
    exec python -m src.bot.main
    ;;

  *)
    echo "[entrypoint] ERROR: SERVICE_TARGET='${SERVICE_TARGET}' no reconocido."
    echo "[entrypoint] Valores válidos: api | bot"
    exit 1
    ;;
esac
