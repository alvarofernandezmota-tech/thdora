#!/bin/sh
# ================================================
# THDORA — Entrypoint API
# ================================================
set -e

echo "🚀 Iniciando THDORA API..."

# Crear directorios necesarios
echo "📁 Preparando directorios..."
mkdir -p /app/data /app/logs
chmod 755 /app/data /app/logs 2>/dev/null || true

# Inicializar base de datos (no bloqueante)
echo "🗄️  Inicializando SQLite en ${THDORA_DB_PATH:-/app/data/thdora.db}..."
python -c '
import sys
try:
    from src.db.base import init_db
    init_db()
    print("✅ DB lista")
except Exception as e:
    print(f"⚠️  Warning en init_db (no bloqueante): {e}")
    sys.exit(0)
'

echo "🌐 Arrancando FastAPI con Uvicorn..."
exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level ${LOG_LEVEL:-info}
