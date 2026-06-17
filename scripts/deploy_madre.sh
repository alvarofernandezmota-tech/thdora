#!/bin/bash
# =============================================================================
# deploy_madre.sh — Despliegue de THDORA en Madre
# Uso: bash scripts/deploy_madre.sh
# Requisitos: git, alembic en PATH (o venv activo), docker compose
# =============================================================================
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()  { echo -e "${GREEN}✅ $*${NC}"; }
info(){ echo -e "${YELLOW}ℹ️  $*${NC}"; }
err(){ echo -e "${RED}❌ $*${NC}"; }

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║   🚀  THDORA — Despliegue en Madre       ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── 1. Directorio del repo ───────────────────────────────────────────────────
REPO_DIR=""
for candidate in ~/thdora /opt/thdora /home/alvaro/thdora; do
    if [ -d "$candidate/.git" ]; then
        REPO_DIR="$candidate"
        break
    fi
done

if [ -z "$REPO_DIR" ]; then
    err "No se encontró el directorio del repo (buscado en ~/thdora, /opt/thdora, /home/alvaro/thdora)"
    err "Clónalo primero: git clone https://github.com/alvarofernandezmota-tech/thdora ~/thdora"
    exit 1
fi

cd "$REPO_DIR"
ok "Repo encontrado en $REPO_DIR"

# ── 2. Activar venv si existe ────────────────────────────────────────────────
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    ok "Virtualenv activado (.venv)"
elif [ -f venv/bin/activate ]; then
    source venv/bin/activate
    ok "Virtualenv activado (venv)"
else
    info "No se encontró venv local — usando Python del sistema/contenedor"
fi

# ── 3. Git pull ──────────────────────────────────────────────────────────────
info "Actualizando código desde GitHub..."
git pull origin main
ok "git pull completado"

# ── 4. Mostrar historial Alembic ─────────────────────────────────────────────
echo ""
info "Historial de migraciones Alembic:"
alembic history
echo ""

# ── 5. Leer down_revision del usuario ────────────────────────────────────────
MIGRATION_FILE="alembic/versions/sprint5_add_user_id_and_allowed_users.py"

# Detectar si ya tiene down_revision real (no None)
CURRENT_DOWN=$(grep 'down_revision' "$MIGRATION_FILE" | head -1)
if echo "$CURRENT_DOWN" | grep -q 'None'; then
    echo -e "${YELLOW}La migración Sprint 5 tiene down_revision = None${NC}"
    read -rp "Pega el ID de la migración anterior (último ID de alembic history, o ENTER para dejar None): " DOWN_REV
    if [ -n "$DOWN_REV" ]; then
        sed -i "s/down_revision = None/down_revision = \"$DOWN_REV\"/" "$MIGRATION_FILE"
        ok "Migración actualizada: down_revision = \"$DOWN_REV\""
    else
        info "Dejando down_revision = None (primera migración de la cadena)"
    fi
else
    info "down_revision ya configurado: $CURRENT_DOWN — sin cambios"
fi

# ── 6. Aplicar migraciones ───────────────────────────────────────────────────
info "Aplicando migraciones..."
alembic upgrade head
ok "Migraciones aplicadas"

# ── 7. Rebuild y restart Docker ──────────────────────────────────────────────
info "Reconstruyendo contenedores Docker..."
docker compose down
docker compose up -d --build
ok "Contenedores levantados"

# ── 8. Logs de verificación ──────────────────────────────────────────────────
info "Esperando 5s para que arranquen los servicios..."
sleep 5
echo ""
echo -e "${YELLOW}📋 Últimos logs:${NC}"
docker compose logs --tail=25

# ── Fin ───────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅  THDORA desplegado correctamente en Madre        ║${NC}"
echo -e "${GREEN}║  🌐  API: http://localhost:8001/docs                  ║${NC}"
echo -e "${GREEN}║  🤖  Bot: activo en Telegram                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
