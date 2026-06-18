#!/bin/sh
# ================================================
# THDORA — Entrypoint Bot
# Espera a que la API esté healthy antes de arrancar
# ================================================
set -e

API_URL="${THDORA_API_URL:-http://thdora:8000}"
MAX_RETRIES=40
RETRY_INTERVAL=3

echo "⏳ Esperando a que la API (${API_URL}) esté lista..."

i=0
while [ $i -lt $MAX_RETRIES ]; do
    if python3 -c "
import urllib.request, sys
try:
    r = urllib.request.urlopen('${API_URL}/health/live', timeout=8)
    sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ API disponible en ${API_URL}"
        break
    fi
    i=$((i + 1))
    echo "   Intento $i/$MAX_RETRIES... (esperando ${RETRY_INTERVAL}s)"
    sleep $RETRY_INTERVAL
done

if [ $i -eq $MAX_RETRIES ]; then
    echo "❌ Timeout: La API no respondió tras $MAX_RETRIES intentos."
    echo "   Revisa los logs con: docker compose logs thdora"
    exit 1
fi

# Preparar directorios
mkdir -p /app/data /app/logs

echo "🤖 Iniciando THDORA Bot..."
exec python -m src.bot.main
