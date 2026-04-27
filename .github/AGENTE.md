# 🤖 Agente THDORA — Automatización del Repo

> **Propósito:** Definir cómo el ecosistema `ai-toolkit` / Perplexity MCP trabaja sobre este repo.
> Cualquier IA con acceso a GitHub MCP puede ejecutar estas tareas.

---

## 🎯 Qué puede automatizar este agente

| Tarea | Cuándo | Resultado |
|---|---|---|
| Crear entrada en `docs/diarios/` | Después de cada sesión de desarrollo | Diario documentado |
| Actualizar `CHANGELOG.md` | Con cada feat/fix | Historial al día |
| Actualizar `ROADMAP.md` | Cuando se completa una fase | Fases marcadas ✅ |

---

## 🔧 Cómo invocarlo

Desde Perplexity MCP o cualquier agente con GitHub MCP:

```
Eres el agente de documentación de THDORA.
Repo: https://github.com/alvarofernandezmota-tech/thdora
Stack: Python + FastAPI + python-telegram-bot v22 + SQLite + Groq
Versión actual: v0.16.0

Tarea hoy:
1. Leer el último commit del repo
2. Crear entrada en docs/diarios/[HOY].md con lo trabajado
3. Actualizar CHANGELOG.md si hay feat/fix nuevos
4. Hacer commit: "docs: sesión [fecha]"
```

---

## 📋 Prompt base para diario de sesión

```
Eres el agente de THDORA. Crea la entrada del diario de hoy:

Archivo: docs/diarios/[FECHA].md

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

## 🔗 Archivos clave del repo

| Archivo | Propósito |
|---|---|
| `CHANGELOG.md` | Historial de versiones |
| `ROADMAP.md` | Fases del proyecto |
| `.github/COMO_PROCEDER.md` | Guía de trabajo activa |
| `docs/diarios/` | Diarios de sesión |
| `src/` | Código fuente (API + Bot) |
| `tests/` | Tests unitarios |

---

_Última actualización: 27 abril 2026 — Perplexity AI MCP_
