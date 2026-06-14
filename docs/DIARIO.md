# 📓 DIARIO DE DESARROLLO — THDORA Ecosystem

> **Diario vivo.** Se actualiza con cada commit relevante.
> Documenta QUÉ se hizo, EN QUÉ RAMA, POR QUÉ, y EN QUÉ ESTADO está.

---

## 📌 Estado actual del ecosistema

| Componente | Rama | Estado | Último cambio |
|---|---|---|---|
| Bot Telegram (THDORA v1) | `main` | ✅ Producción 24/7 | — |
| Agent Platform v2 scaffold | `feature/agent-platform-v2` | 🔨 En desarrollo | 2026-06-15 |

---

## 2026-06-15 — Scaffold Agent Platform v2

**Rama:** `feature/agent-platform-v2`  
**Tipo:** `feat`  
**Estado:** 🔨 Scaffold creado, pendiente de arrancar y probar

### Qué se hizo
- Creada rama `feature/agent-platform-v2` desde `main`
- Subido scaffold completo de la plataforma de agentes en `platform/`
- **NO toca el bot actual** — puertos distintos, BD distinta, servicio independiente

### Qué incluye
- `platform/migrations/001_initial_schema.sql` — DDL completo (tenants, agents, tools, messages + pgvector)
- `platform/core/` — Config, DB async, Redis cache
- `platform/agents/` — Models SQLAlchemy, Schemas Pydantic, CRUD, **LangGraph Orchestrator**
- `platform/tools/` — Tool Registry dinámico + implementaciones (telegram, http)
- `platform/api/` — Endpoints FastAPI: POST /agents/, POST /chat/{agent_id}, Tool Registry
- `platform/docker-compose.platform.yml` — Stack completo aislado

### Por qué existe
Convertir THDORA de bot personal a plataforma multi-tenant de agentes clonables.
Cualquier persona puede crear un agente nuevo cambiando solo system_prompt + tools, sin tocar código.

### Cómo arrancar
```bash
git checkout feature/agent-platform-v2
cd platform && cp .env.example .env
# Rellenar GROQ_API_KEY y TELEGRAM_BOT_TOKEN en .env
docker compose -f docker-compose.platform.yml up -d
uvicorn main:app --reload
```

### Próximos pasos en esta rama
- [ ] Arrancar y verificar que el schema se aplica
- [ ] Probar endpoint POST /agents/ via Swagger (localhost:8001/docs)
- [ ] Probar POST /chat/{agent_id} con un agente de prueba
- [ ] Migrar lógica del bot actual al orquestador

---

## 2026-06-15 — Documentación maestra creada

**Rama:** `main`  
**Tipo:** `docs`  
**Estado:** ✅ Activo

### Qué se hizo
- Creada estructura `docs/` en `main`
- `DIARIO.md` — este archivo, diario vivo del ecosistema
- `ECOSYSTEM.md` — mapa completo del ecosistema: qué es cada cosa, para qué sirve
- `BRANCHES.md` — guía de ramas activas, su propósito y estado

### Por qué existe
El proyecto crece en múltiples ramas y direcciones. Sin documentación viva se pierde el hilo.
Este sistema garantiza que en cualquier momento se puede saber exactamente:
- Qué funciona y qué no
- En qué rama está cada cosa
- Por qué se tomó cada decisión

---

<!-- PLANTILLA para nuevas entradas —————————————————————————

## YYYY-MM-DD — Título del cambio

**Rama:** `nombre-rama`
**Tipo:** `feat` | `fix` | `docs` | `refactor` | `test`
**Estado:** ✅ Activo | 🔨 En desarrollo | ⏸ Pausado | ❌ Descartado

### Qué se hizo

### Por qué existe

### Cómo probarlo

### Próximos pasos

————————————————————————————————————————————————————————————— -->
