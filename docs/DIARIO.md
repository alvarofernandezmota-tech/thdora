# 📓 DIARIO DE DESARROLLO — THDORA Ecosystem

> **Diario vivo.** Se actualiza con cada commit relevante.
> Documenta QUÉ se hizo, EN QUÉ RAMA, POR QUÉ, y EN QUÉ ESTADO está.

---

## 📌 Estado actual del ecosistema

| Componente | Rama | Estado | Último cambio |
|---|---|---|---|
| Bot Telegram (THDORA v1) | `main` | ✅ Producción 24/7 | 18 jun 2026 |
| Agent Platform v2 scaffold | `feature/agent-platform-v2` | 🔨 En desarrollo | 2026-06-15 |

---

## 2026-06-18 — Troubleshooting arranque en máquina nueva + fix langgraph

**Rama:** `main`
**Tipo:** `fix` + `docs`
**Estado:** ⏳ Pendiente rebuild Docker en máquina local

### Qué se hizo
- Resueltos 4 bugs encadenados al clonar y levantar el stack en máquina nueva (`madre`)
- Fix de dependencia: `langgraph-checkpoint-sqlite>=2.0.0` añadido a `requirements.txt` y `pyproject.toml`
- Documentación completa en `docs/sesiones/2026-06-18-docker-nueva-maquina.md`
- Creada guía `docs/setup/nueva-maquina.md` para futuros arranques
- Entrada `v0.21.3` en `CHANGELOG.md`

### Bugs resueltos (en orden)
1. `ImportError: cannot import name '_invalidate_cache'` → imagen Docker desactualizada, fix: rebuild
2. `fatal: not a git repository` → ejecutar comandos fuera de la carpeta del repo
3. `.env not found` → el `.env` no se copia al hacer clone nuevo
4. `ModuleNotFoundError: langgraph.checkpoint.sqlite` → paquete separado no estaba en deps

### Comandos para retomar
```bash
cd ~/Projects/thdora
git pull origin main
docker compose build bot
docker compose up -d bot
docker compose logs -f bot
```

### Próximos pasos
- [ ] Rebuild Docker en máquina y verificar que bot arranca sin errores
- [ ] Smoke test completo del agente LangGraph con memoria persistente
- [ ] Verificar `/health/live` y Prometheus

---

## 2026-06-17 — Deploy stack completo dockerizado

**Rama:** `main`
**Tipo:** `feat` + `fix`
**Estado:** ✅ Activo

### Qué se hizo
- Stack completo (API + Bot + Prometheus + Grafana) levantado en Docker Compose
- Resueltos 6 bugs de infraestructura encadenados
- Creado `scripts/deploy.sh` reproducible

### Ver detalle
Ver `CHANGELOG.md` — entrada `v0.21.2`

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

<!-- PLANTILLA para nuevas entradas —————————————————————————————

## YYYY-MM-DD — Título del cambio

**Rama:** `nombre-rama`
**Tipo:** `feat` | `fix` | `docs` | `refactor` | `test`
**Estado:** ✅ Activo | 🔨 En desarrollo | ⏸ Pausado | ❌ Descartado

### Qué se hizo

### Por qué existe

### Cómo probarlo

### Próximos pasos

————————————————————————————————————————————————————————— -->
