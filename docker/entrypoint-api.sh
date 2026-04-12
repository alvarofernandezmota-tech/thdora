#!/bin/sh
# Entrypoint del servicio `api`
# 1. Inicializa la base de datos SQLite si no existe
# 2. Arranca uvicorn en modo producción (sin --reload)
set -e

echo "🗄️  Inicializando base de datos en ${THDORA_DB_PATH:-/app/data/thdora.db}..."
python -c "
from src.db.base import init_db
init_db()
print('✅ DB lista')
"

echo "🚀 Arrancando THDORA API en 0.0.0.0:8000..."
exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info
