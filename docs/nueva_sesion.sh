#!/bin/bash
# ─────────────────────────────────────────────────────────────
# nueva_sesion.sh — genera commit de documentación automático
# Uso: ./docs/nueva_sesion.sh "Descripción breve de la sesión"
# ─────────────────────────────────────────────────────────────

set -e

FECHA=$(date '+%Y-%m-%d')
HORA=$(date '+%H:%M')
COMMIT=$(git rev-parse --short HEAD)
RAMA=$(git branch --show-current)
DESCRIPCION=${1:-"Sesión de desarrollo"}
ARCHIVO="docs/sesiones/${FECHA}.md"

mkdir -p docs/sesiones

cat >> "$ARCHIVO" << EOF

## Sesión ${FECHA} ${HORA} — ${DESCRIPCION}
- Rama: ${RAMA}
- Commit: ${COMMIT}
- Archivos modificados: $(git diff --name-only HEAD~1 HEAD 2>/dev/null | wc -l | tr -d ' ')

### Archivos
$(git diff --name-only HEAD~1 HEAD 2>/dev/null | sed 's/^/- /')

### Notas
<!-- Añadir notas manualmente aquí -->

EOF

git add "$ARCHIVO"
git commit -m "docs: auto-sesión ${FECHA} — ${DESCRIPCION}"

echo "✅ Sesión documentada en ${ARCHIVO}"
echo "📤 Haz git push para subir al repo"
