# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md) · [Setup entorno](docs/setup/entorno-local.md)

## Estado: v0.4.0 — 24 marzo 2026

```
[████████████████████████] 100% ✅ FASE 1: Interfaces abstractas (AbstractLifeManager)
[████████████████████████] 100% ✅ FASE 2: MemoryLifeManager (CRUD en memoria)
[████████████████████████] 100% ✅ FASE 3: Bot CLI interactivo
[███████████████████████▀]  95% 🔄 FASE 4: Monorepo enterprise + docs exhaustivos
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 5: Persistencia JSON + tests unitarios
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 6: FastAPI REST
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 7: Bot Telegram
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 8: Ollama IA local (qwen2.5-coder:7b + CUDA)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 9: OpenClaw + agentes IA (migración thea-ia)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 10: CI/CD + Docker + Deploy
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 11: BD real (migración SQLAlchemy de thea-ia)
```

---

## ✅ FASE 1-3 — Completadas

- `AbstractLifeManager` — interfaz ABC con citas + hábitos
- `MemoryLifeManager` — implementación en memoria con UUID, 13 tests passing
- Bot CLI interactivo con menú

📚 Docs: [core.md](docs/modules/core.md)

---

## 🔄 FASE 4 — Monorepo enterprise + docs (95%)

- [x] Migración AppointmentManager → `src/core/`
- [x] Estructura enterprise completa
- [x] Documentación de interfaces y módulos
- [x] `pyproject.toml` completo
- [x] `Makefile` con comandos de desarrollo
- [x] ADR-001 Monorepo
- [x] ADR-002 ABC Interfaces
- [x] ADR-003 JSON Persistence
- [x] ADR-004 Relación thea-ia
- [x] Auditoría thea-ia completa
- [x] Setup entorno local documentado (WSL2 + OpenClaw + Ollama + Telegram + CUDA)
- [x] README con navegación rápida
- [x] Índice maestro de docs
- [ ] Diario 2026-03-24 completado al cierre del día

📚 Docs: [INDEX.md](docs/INDEX.md) · [ADRs](docs/architecture/decisions/) · [Auditoría thea-ia](docs/auditoria/thea-ia.md)

---

## ⏳ FASE 5 — Persistencia JSON + Tests

**Objetivo:** thdora recuerda cosas entre reinicios. Primera persistencia real.

- [ ] `src/core/impl/json_lifemanager.py` — `JsonLifeManager` implementado
- [ ] `datos/thdora.json` — fichero de datos (en `.gitignore`)
- [ ] Tests unitarios `JsonLifeManager` con pytest
- [ ] Coverage >80%
- [ ] Pre-commit hooks

📚 Docs: [ADR-003 JSON Persistence](docs/architecture/decisions/ADR-003-json-persistence.md)  
🔍 Referencia thea-ia: [`src/theaia/models/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/models)

---

## ⏳ FASE 6 — FastAPI REST

**Objetivo:** thdora tiene API. Cualquier cliente puede consultar citas y hábitos.

- [ ] `GET /appointments/{date}` — citas del día
- [ ] `POST /appointments` — crear cita
- [ ] `DELETE /appointments/{id}` — eliminar
- [ ] `GET /habits/{date}` — hábitos del día
- [ ] `POST /habits` — registrar hábito
- [ ] `GET /summary/{date}` — resumen del día
- [ ] Swagger UI automático
- [ ] Pydantic models

📚 Docs: [api.md](docs/modules/api.md)  
🔍 Referencia thea-ia: [`src/theaia/api/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/api)

---

## ⏳ FASE 7 — Bot Telegram

**Objetivo:** thdora accesible desde el móvil. Primer uso real del sistema.

- [ ] Setup `python-telegram-bot`
- [ ] `/citas` — ver citas del día
- [ ] `/nueva` — crear cita (ConversationHandler)
- [ ] `/habito` — registrar hábito
- [ ] `/resumen` — resumen del día
- [ ] Notificaciones automáticas 15 min antes

🔍 Referencia thea-ia: [`src/theaia/adapters/telegram/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/adapters/telegram) — `bot.py` (8KB) + `telegram_adapter.py` (14KB)

---

## ⏳ FASE 8 — Ollama IA local

**Hardware:** GTX 1060 6GB VRAM + 16GB RAM + CUDA  
**Modelo principal:** `qwen2.5-coder:7b` (~4.7GB VRAM) — especializado en código  
**Modelo rápido (opcional):** `phi3.5:3.8b` (~2.3GB VRAM)

- [ ] Activar CUDA en WSL2 (ver [Setup entorno §4.4](docs/setup/entorno-local.md#44-activar-cuda-en-wsl2-gtx-1060))
- [ ] Verificar `ollama ps` → `100% GPU`
- [ ] `src/ai/ollama_client.py` — cliente Ollama
- [ ] Conectar con bot Telegram
- [ ] Comando `/pregunta <texto>` en el bot

📚 Docs: [Setup entorno](docs/setup/entorno-local.md)  
🔍 Referencia thea-ia: [`src/theaia/core/nlp_engine.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/nlp_engine.py) (15KB)

---

## ⏳ FASE 9 — OpenClaw + Agentes IA

**Objetivo:** thdora controla repos GitHub desde Telegram. OpenClaw integrado como agente.

- [ ] Integrar OpenClaw gateway con el bot Telegram de thdora
- [ ] Agente GitHub: leer issues, PRs, commits desde Telegram
- [ ] Agente thdora: gestionar citas/hábitos con lenguaje natural
- [ ] Orquestador de agentes

🔍 Referencia thea-ia: [`src/theaia/core/orchestrator.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/orchestrator.py) (14KB) · [`router.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/router.py) (14KB)

---

## ⏳ FASE 10 — CI/CD + Docker

- [ ] GitHub Actions — tests automáticos en cada push
- [ ] GitHub Actions — linting (black + flake8)
- [ ] `Dockerfile` + `docker-compose.yml`
- [ ] Deploy en Railway/VPS

---

## ⏳ FASE 11 — Base de datos real

**Objetivo:** migrar de JSON a SQLite/PostgreSQL cuando el sistema lo requiera.

- [ ] Evaluar SQLite vs PostgreSQL
- [ ] `SqlLifeManager` implementado con SQLAlchemy
- [ ] Migraciones con Alembic
- [ ] Tests de migración JSON → SQL

🔍 Referencia thea-ia: [`src/theaia/database/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/database) — SQLAlchemy + Alembic ya implementados

---

_Actualizado: 24 marzo 2026_
