#!/bin/sh
# Entrypoint del servicio `bot`
# Espera a que la API responda 200 en /health/live antes de arrancar el bot.
set -e

API_URL="${THDORA_API_URL:-http://thdora:8000}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "⏳ Esperando a que la API esté disponible en ${API_URL}/health/live..."
i=0
while [ $i -lt $MAX_RETRIES ]; do
    if python3 -c "
import urllib.request, sys
try:
    r = urllib.request.urlopen('${API_URL}/health/live', timeout=5)
    sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ API disponible"
        break
    fi
    i=$((i + 1))
    echo "   Intento $i/$MAX_RETRIES... reintentando en ${RETRY_INTERVAL}s"
    sleep $RETRY_INTERVAL
done

if [ $i -eq $MAX_RETRIES ]; then
    echo "❌ La API no respondió tras $MAX_RETRIES intentos. Abortando."
    exit 1
fi

echo "🤖 Arrancando THDORA Bot..."
exec python -m src.bot.main
