# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md)

## Estado: v0.6.0 — 25 marzo 2026

```
[████████████████████████] 100% ✅ FASE 1: Setup inicial + estructura enterprise
[████████████████████████] 100% ✅ FASE 2: Interfaces ABC + MemoryLifeManager
[████████████████████████] 100% ✅ FASE 3: Monorepo enterprise + docs + ADRs
[████████████████████████] 100% ✅ FASE 4: MemoryLifeManager completo + tests unitarios
[████████████████████████] 100% ✅ FASE 5: JsonLifeManager + persistencia + tests
[████████████████████████] 100% ✅ FASE 6: FastAPI REST + tests integración + docs
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 7: Bot Telegram ← SIGUIENTE
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 8: Ollama IA local (mistral/qwen2.5 + CUDA)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 9: OpenClaw + agentes IA (migración thea-ia)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 10: CI/CD + Docker + Deploy
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 11: BD real (SQLAlchemy + Alembic)
```

---

## ✅ FASES 1-6 — Completadas (v0.6.0)

### Fase 1 — Setup
- `pyproject.toml`, `Makefile`, `.gitignore`, estructura de directorios

### Fase 2 — Core inicial
- `AbstractLifeManager` — interfaz ABC con métodos abstractos
- `MemoryLifeManager` — implementación en memoria

### Fase 3 — Monorepo enterprise
- ADR-001 Monorepo, ADR-002 ABC, ADR-003 JSON, ADR-004 thea-ia
- `docs/INDEX.md`, setup entorno local (WSL2 + Ollama + Telegram + CUDA)
- Auditoría thea-ia completa

### Fase 4 — MemoryLifeManager completo
- Validación hora (`HH:MM`) y tipo (`VALID_TYPES`)
- 13 tests unitarios pasando, coverage 100%

### Fase 5 — JsonLifeManager + persistencia
- `src/core/impl/json_lifemanager.py` — implementado y testeado
- `datos/thdora.json` — datos reales (en `.gitignore`)
- 18 tests unitarios pasando, coverage 100%

### Fase 6 — FastAPI REST
- 6 endpoints implementados y testeados
- Pydantic models, dependency injection
- 16 tests de integración pasando, coverage 100% en routers

📊 Coverage total: **87%** — 57/57 tests pasando

---

## ⏳ FASE 7 — Bot Telegram ← ACTIVA

**Objetivo:** thdora accesible desde el móvil. Primer uso real del sistema.

### Paso previo (API)
- [ ] `GET /summary/{date}` — añadir endpoint de resumen diario
- [ ] Test de integración del nuevo endpoint

### Fase 7a — Comandos explícitos
- [ ] Setup `python-telegram-bot` en `src/bot/`
- [ ] `/hoy` — resumen del día (citas + hábitos)
- [ ] `/citas` — listar citas del día
- [ ] `/cita` — crear cita (ConversationHandler)
- [ ] `/borrar_cita` — eliminar cita por índice
- [ ] `/habitos` — listar hábitos del día
- [ ] `/habito` — registrar hábito
- [ ] `TELEGRAM_TOKEN` en `.env`

### Fase 7b — Lenguaje natural básico
- [ ] Detección de intención por regex/patrones
- [ ] "cita médica mañana a las 10" → `/cita`
- [ ] "dormí 7 horas" → `/habito sueno 7h`

🔍 Referencia thea-ia: [`src/theaia/adapters/telegram/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/adapters/telegram)

---

## ⏳ FASE 8 — Ollama IA local

**Hardware:** GTX 1060 6GB VRAM + 16GB RAM + CUDA  
**Modelo:** `mistral-nemo:12b` o `qwen2.5-coder:7b` según VRAM disponible

- [ ] Activar CUDA en WSL2
- [ ] `src/ai/ollama_client.py` — cliente Ollama
- [ ] Extraer NLP engine de thea-ia
- [ ] Conectar con bot Telegram: `/pregunta <texto>`
- [ ] Extracción de intención + parámetros vía IA

🔍 Referencia thea-ia: [`src/theaia/core/nlp_engine.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/nlp_engine.py) (15KB)

---

## ⏳ FASE 9 — OpenClaw + Agentes IA

- [ ] Integrar OpenClaw gateway con el bot
- [ ] Agente GitHub: issues, PRs, commits desde Telegram
- [ ] Orquestador de agentes (migrar de thea-ia)

🔍 Referencia thea-ia: [`orchestrator.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/orchestrator.py) · [`router.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/router.py)

---

## ⏳ FASE 10 — CI/CD + Docker

- [ ] GitHub Actions — tests automáticos en cada push
- [ ] `Dockerfile` + `docker-compose.yml`
- [ ] Deploy en Railway/VPS

---

## ⏳ FASE 11 — Base de datos real

- [ ] `SqlLifeManager` con SQLAlchemy
- [ ] Migraciones con Alembic
- [ ] Migración JSON → SQL

🔍 Referencia thea-ia: [`src/theaia/database/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/database)

---

_Actualizado: 25 marzo 2026 — 10:21 CET_
