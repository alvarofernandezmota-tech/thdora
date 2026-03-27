# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md) · [Personal Data Platform](docs/PERSONAL-DATA-PLATFORM.md)

## Estado: v0.6.1 — 25 marzo 2026

```
[████████████████████████] 100% ✅ FASE 1: Setup inicial + estructura enterprise
[████████████████████████] 100% ✅ FASE 2: Interfaces ABC + MemoryLifeManager
[████████████████████████] 100% ✅ FASE 3: Monorepo enterprise + docs + ADRs
[████████████████████████] 100% ✅ FASE 4: MemoryLifeManager completo + tests unitarios
[████████████████████████] 100% ✅ FASE 5: JsonLifeManager + persistencia + tests
[████████████████████████] 100% ✅ FASE 6: FastAPI REST (7 endpoints) + tests + docs
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 7: Bot Telegram ← SIGUIENTE
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 8: Ollama IA local (mistral/qwen2.5 + CUDA)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 9: OpenClaw + agentes IA (migración thea-ia)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 10: CI/CD + Docker + Deploy
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 11: BD real (SQLAlchemy + Alembic)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 12: Personal Data Platform — sync YAML → SQLite
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 13: Bot tracking — /stats /habitos /nota-hoy + alertas
```

---

## ✅ FASES 1-6 — Completadas (v0.6.1)

### Resumen
- Core: `AbstractLifeManager`, `MemoryLifeManager` (100% cov), `JsonLifeManager` (100% cov)
- API: 7 endpoints REST, Pydantic models, dependency injection, Swagger UI
- Tests: 57/57 pasando | Coverage: 87%
- Docs: arquitectura, módulos, setup, auditoría, diarios

### Endpoints API (Fase 6)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/appointments/{date}` | Crear cita |
| `GET` | `/appointments/{date}` | Listar citas |
| `DELETE` | `/appointments/{date}/{index}` | Eliminar cita |
| `POST` | `/habits/{date}` | Registrar hábito |
| `GET` | `/habits/{date}` | Listar hábitos |
| `GET` | `/summary/{date}` | Resumen del día |

---

## ⏳ FASE 7 — Bot Telegram ← ACTIVA

**Objetivo:** thdora accesible desde el móvil. Primer uso real del sistema.

### Primer paso
- [ ] Test de integración para `GET /summary/{date}`

### Fase 7a — Comandos explícitos (6 comandos)
- [ ] Setup `python-telegram-bot` en `src/bot/`
- [ ] `/hoy` — resumen del día
- [ ] `/citas` — listar citas
- [ ] `/cita` — crear cita
- [ ] `/borrar_cita` — eliminar cita
- [ ] `/habitos` — listar hábitos
- [ ] `/habito` — registrar hábito
- [ ] `TELEGRAM_TOKEN` en `.env`

### Fase 7b — Lenguaje natural básico
- [ ] Detección de intención por regex
- [ ] "cita médica mañana a las 10" → `/cita`
- [ ] "dormí 7 horas" → `/habito sueno 7h`

🔍 Referencia thea-ia: [`src/theaia/adapters/telegram/`](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/adapters/telegram)

---

## ⏳ FASE 8 — Ollama IA local

**Hardware:** GTX 1060 6GB VRAM + 16GB RAM + CUDA  
**Modelo:** `mistral-nemo:12b` o `qwen2.5-coder:7b`

- [ ] Activar CUDA en WSL2
- [ ] `src/ai/ollama_client.py`
- [ ] Extraer NLP engine de thea-ia
- [ ] `/pregunta <texto>` en el bot

🔍 Referencia thea-ia: [`nlp_engine.py`](https://github.com/alvarofernandezmota-tech/thea-ia/blob/main/src/theaia/core/nlp_engine.py)

---

## ⏳ FASES 9–11

- **Fase 9** — OpenClaw + agentes IA (orquestador de thea-ia)
- **Fase 10** — CI/CD + Docker + Deploy
- **Fase 11** — SQLAlchemy + Alembic (migración desde thea-ia)

---

## ⏳ FASE 12 — Personal Data Platform — sync YAML → SQLite

**Objetivo:** Convertir thdora en el motor del ecosistema de tracking personal de Álvaro.  
**Dependencias:** Fase 11 (SQLAlchemy) + Fase 7 (Bot Telegram)  
**Docs completos:** [docs/PERSONAL-DATA-PLATFORM.md](docs/PERSONAL-DATA-PLATFORM.md)

### Arquitectura
```
repo personal/ — YAML diarios (fuente de verdad humana)
        ↓
sync_tracking.py — lee YAMLs, valida schema, inserta en BD
        ↓
SQLite (thdora) — datos estructurados, consultas rápidas
        ↓
thdora API — nuevos endpoints /tracking/*
```

### Tareas F12
- [ ] `src/tracking/models.py` — modelo SQLAlchemy `DailyRecord`
- [ ] `src/tracking/sync.py` — lee YAML via GitHub API o ruta local
- [ ] `src/tracking/parser.py` — valida y transforma YAML → `DailyRecord`
- [ ] `GET /tracking/semana/{num}` — métricas automáticas de una semana
- [ ] `GET /tracking/mes/{num}` — métricas de un mes
- [ ] Tests unitarios del parser y sync

**Semana estimada:** S14

---

## ⏳ FASE 13 — Bot tracking — /stats /habitos /nota-hoy + alertas

**Objetivo:** El bot Telegram responde preguntas de tracking y manda alertas proactivas.  
**Dependencias:** Fase 7 (Bot) + Fase 12 (PDP)

### Comandos nuevos
- [ ] `/stats` — resumen semanal completo (notas, estudio, sueño, sustancias)
- [ ] `/habitos` — estado de hábitos de la semana actual
- [ ] `/nota-hoy` — calcula nota del día automáticamente
- [ ] `/racha` — rachas activas (días sin cocaína, ejercicio consecutivo, etc.)

### Alertas automáticas (scheduler)
- [ ] "Llevas 3 días sin ejercicio ⚠️"
- [ ] "Ayer dormiste menos de 5h 😴"
- [ ] "Esta semana vas bien en estudio 📚 +2h respecto S anterior"
- [ ] Recordatorio nocturno: "Rellena el YAML de hoy"

**Semana estimada:** S15

---

_Actualizado: 27 marzo 2026 17:42 CET — Fases 12-13 Personal Data Platform añadidas_
