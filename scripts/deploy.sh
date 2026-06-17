#!/bin/bash
# =============================================================================
# deploy.sh — Despliegue limpio y reproducible de THDORA
#
# Uso:
#   bash scripts/deploy.sh             # despliegue normal (con rebuild)
#   bash scripts/deploy.sh --no-build  # reutiliza imagen existente
#
# Qué hace (en orden):
#   1. Descarta cambios locales y sincroniza con origin/main
#   2. Crea ./data y ./logs con los permisos correctos (UID 1000)
#   3. docker compose up --build
#   4. Muestra logs de arranque para verificar el estado
# =============================================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅  $*${NC}"; }
info() { echo -e "${YELLOW}ℹ️   $*${NC}"; }
err()  { echo -e "${RED}❌  $*${NC}"; exit 1; }

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║   🚀  THDORA — Deploy                   ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── 0. Argumentos ─────────────────────────────────────────────────────────────────────────────
BUILD_FLAG="--build"
for arg in "$@"; do
    [ "$arg" = "--no-build" ] && BUILD_FLAG=""
done

# ── 1. Directorio del repo ────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR"
ok "Directorio del repo: $REPO_DIR"

# ── 2. Comprobaciones previas ───────────────────────────────────────────────────────────────────
command -v git         >/dev/null 2>&1 || err "git no encontrado"
command -v docker      >/dev/null 2>&1 || err "docker no encontrado"
docker compose version >/dev/null 2>&1 || err "docker compose v2 no encontrado"
[ -f .env ]            || err "Falta el fichero .env — cópialo desde .env.example"

# ── 3. Sincronizar con origin/main ────────────────────────────────────────────────────────────────
info "Sincronizando con origin/main..."
git fetch --quiet origin
git reset --hard origin/main
ok "Código sincronizado con origin/main"

# ── 4. Permisos de ./data y ./logs ───────────────────────────────────────────────────────────────
info "Ajustando permisos de ./data y ./logs (UID 1000)..."
mkdir -p ./data ./logs
if sudo chown -R 1000:1000 ./data ./logs 2>/dev/null; then
    ok "chown aplicado (sudo)"
else
    chown -R 1000:1000 ./data ./logs && ok "chown aplicado" \
        || info "No se pudo hacer chown — comprueba permisos manualmente"
fi

# ── 5. Docker Compose ─────────────────────────────────────────────────────────────────────────────
info "Deteniendo servicios actuales..."
docker compose down --remove-orphans 2>/dev/null || true

info "Levantando stack${BUILD_FLAG:+ (con rebuild)}..."
# shellcheck disable=SC2086
docker compose up -d $BUILD_FLAG
ok "Stack levantado"

# ── 6. Verificación ────────────────────────────────────────────────────────────────────────────────
info "Esperando 10s para que arranquen los servicios..."
sleep 10

echo ""
echo -e "${YELLOW}📋 Estado de los contenedores:${NC}"
docker compose ps

echo ""
echo -e "${YELLOW}📋 Logs thdora (últimas 20 líneas):${NC}"
docker compose logs --tail=20 thdora

echo ""
echo -e "${YELLOW}📋 Logs bot (últimas 20 líneas):${NC}"
docker compose logs --tail=20 bot 2>/dev/null || true

# ── 7. Health check rápido ─────────────────────────────────────────────────────────────────────────────
echo ""
info "Comprobando /health/live..."
if python3 -c "
import urllib.request, sys
try:
    r = urllib.request.urlopen('http://localhost:8000/health/live', timeout=5)
    sys.exit(0 if r.status == 200 else 1)
except Exception as e:
    print(e); sys.exit(1)
" 2>/dev/null; then
    ok "API responde en http://localhost:8000/health/live"
else
    echo -e "${YELLOW}⚠️  /health/live aún no responde — revisa los logs arriba${NC}"
fi

# ── Fin ────────────────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╝${NC}"
echo -e "${GREEN}║  ✅  THDORA desplegado                           ║${NC}"
echo -e "${GREEN}║  🌐  API:      http://localhost:8000/docs        ║${NC}"
echo -e "${GREEN}║  ❤️   Health:   http://localhost:8000/health/live ║${NC}"
echo -e "${GREEN}║  📊  Metrics:  http://localhost:8000/metrics     ║${NC}"
echo -e "${GREEN}║  📈  Prom:     http://localhost:9090             ║${NC}"
echo -e "${GREEN}║  📉  Grafana:  http://localhost:3000             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
