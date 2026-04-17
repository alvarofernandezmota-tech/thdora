# 🤖 Agente THDORA — Automatización del Repo

> **Propósito:** Definir cómo el ecosistema `ai-toolkit` trabaja sobre este repo.
> Cualquier IA con acceso a GitHub MCP o OpenCode puede ejecutar estas tareas.

---

## 🎯 Qué puede automatizar este agente

| Tarea | Cuándo | Resultado |
|---|---|---|
| Crear entrada en `docs/diario/` | Después de cada sesión de desarrollo | Diario de sesión documentado |
| Actualizar `CHANGELOG.md` | Con cada feat/fix | Historial al día |
| Actualizar `COMO_PROCEDER.md` | Cuando cambia el plan | Guía de trabajo actualizada |
| Actualizar `ROADMAP.md` | Cuando se completa una fase | Fases marcadas ✅ |
| Crear entrada diario sesión | Al terminar de trabajar | `docs/diario/YYYY-MM-DD.md` |

---

## 🔧 Cómo invocarlo desde ai-toolkit

```bash
# Desde ~/projects/ai-toolkit
bash scripts/agente-thdora.sh
```

O directamente en OpenCode:

```
Eres el agente de documentación de THDORA.
Repo: https://github.com/alvarofernandezmota-tech/thdora
Stack: Python + FastAPI + python-telegram-bot v22 + SQLite
Versión actual: v4.1.0

Tarea hoy:
1. Leer el último commit del repo
2. Crear entrada en docs/diario/[HOY].md con lo trabajado
3. Actualizar CHANGELOG.md si hay feat/fix nuevos
4. Hacer commit: "docs: sesión [fecha]"
```

---

## 📋 Prompt base para diario de sesión

```
Eres el agente de THDORA. Crea la entrada del diario de hoy:

Archivo: docs/diario/[FECHA].md

Estructura:
## Sesión [FECHA]

### ✅ Completado
- [lista]

### 🐛 Bugs resueltos
- [lista]

### 🔧 Cambios técnicos
- [lista de archivos modificados y por qué]

### 📌 Siguiente sesión
- [1-3 tareas concretas]

### Estado general
- Versión: vX.Y.Z
- Tests: ✅/❌
- Docker: ✅/❌
```

---

## 📋 Prompt base para actualizar CHANGELOG

```
Lee los últimos commits de THDORA y actualiza CHANGELOG.md.

Formato de entrada:
## [vX.Y.Z] — YYYY-MM-DD
### Added / Fixed / Changed
- descripción del cambio

Reglas:
- Un commit = una línea en el CHANGELOG
- Agrupa por tipo: feat→Added, fix→Fixed, refactor→Changed
- No duplicar entradas existentes
```

---

## 🔗 Archivos clave del repo

| Archivo | Propósito |
|---|---|
| `CHANGELOG.md` | Historial de versiones |
| `ROADMAP.md` | Fases del proyecto |
| `COMO_PROCEDER.md` | Guía de trabajo activa |
| `docs/diario/` | Diarios de sesión |
| `src/` | Código fuente (API + Bot) |
| `tests/` | Tests unitarios |

---

## ⚙️ Script pendiente en ai-toolkit

`scripts/agente-thdora.sh` — lanza OpenCode con contexto de THDORA:

```bash
#!/bin/bash
export REPO_URL="https://github.com/alvarofernandezmota-tech/thdora"
export REPO_NAME="thdora"
export REPO_STACK="Python FastAPI python-telegram-bot SQLite"
export REPO_VERSION="v4.1.0"
cd ~/projects/ai-toolkit
opencode --model groq/llama-3.3-70b
```

---

_Creado: 17 abril 2026 — por Perplexity AI MCP_
