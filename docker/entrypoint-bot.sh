#!/bin/sh
# Entrypoint del servicio `bot`
# Espera a que la API responda con 200 antes de arrancar el bot.
# El health check de Docker ya garantiza esto via depends_on: condition: service_healthy
# pero este script añade una capa extra para entornos sin Compose.
set -e

API_URL="${THDORA_API_URL:-http://api:8000}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "⏳ Esperando a que la API esté disponible en ${API_URL}/health..."
i=0
while [ $i -lt $MAX_RETRIES ]; do
    if python -c "
import urllib.request, sys
try:
    urllib.request.urlopen('${API_URL}/health')
    sys.exit(0)
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
