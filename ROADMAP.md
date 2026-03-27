# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md) · [Arquitectura](docs/architecture/ARCHITECTURE.md) · [Personal Data Platform](docs/PERSONAL-DATA-PLATFORM.md)

## Estado: v0.7.0 — 27 marzo 2026

```
[████████████████████████] 100% ✅ FASE 1: Setup inicial + estructura enterprise
[████████████████████████] 100% ✅ FASE 2: Interfaces ABC + MemoryLifeManager
[████████████████████████] 100% ✅ FASE 3: Monorepo enterprise + docs + ADRs
[████████████████████████] 100% ✅ FASE 4: MemoryLifeManager completo + tests unitarios
[████████████████████████] 100% ✅ FASE 5: JsonLifeManager + persistencia + tests
[████████████████████████] 100% ✅ FASE 6: FastAPI REST (7 endpoints) + tests + docs
[███████████████▌░░░░░░░░]  60% 🔄 FASE 7: Bot Telegram ← EN PROGRESO
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 8: Ollama IA local (mistral/qwen2.5 + CUDA)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 9: OpenClaw + agentes IA (migración thea-ia)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 10: CI/CD + Docker + Deploy
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 11: BD real (SQLAlchemy + Alembic)
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 12: Personal Data Platform — sync YAML → SQLite
[░░░░░░░░░░░░░░░░░░░░░░░░]   0% ⏳ FASE 13: Bot tracking — /stats /nota-hoy /racha + alertas
```

---

## ✅ FASES 1–6 — Completadas (v0.6.1)

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

## 🔄 FASE 7 — Bot Telegram ← EN PROGRESO (v0.7.0)

**Objetivo:** thdora accesible desde el móvil. Primer uso real del sistema.

### F7a — Bot base ✅ COMPLETADO (27 marzo 2026)
- [x] `src/bot/api_client.py` — cliente HTTP asíncrono completo
- [x] `src/bot/handlers.py` — todos los comandos básicos
- [x] `src/bot/main.py` — arranca, lee `.env`, comprueba API
- [x] `/start`, `/citas`, `/habitos`, `/resumen` — funcionan
- [x] `/nueva` y `/habito` — ConversationHandlers (flujos básicos)
- [x] `deps.py` — singleton del manager (en desarrollo)

### F7b — Sistema mejorado 🔄 EN DESARROLLO (hoy noche)

Rediseño del sistema de interacción con mejoras importantes:

**API — nuevos endpoints:**
- [ ] `PUT /appointments/{date}/{index}` — editar cita
- [ ] `DELETE /habits/{date}/{habit}` — borrar hábito
- [ ] `PUT /habits/{date}/{habit}` — editar hábito

**Bot — flujos mejorados:**
- [ ] Fechas y horas **flexibles** con `dateparser` (`hoy`, `mañana`, `9am`, `27/03`)
- [ ] `/nueva` con **5 pasos** (+ nombre/descripción de la cita)
- [ ] `/citas` con **botones inline** por cada cita (🗑️ Borrar / ✏️ Editar)
- [ ] `/habitos` con **botones inline** por cada hábito (🗑️ Borrar / ✏️ Editar / ➕ Sumar)
- [ ] Hábitos **acumulables**: `+2L` suma al valor existente con detección de unidades
- [ ] **Confirmación** antes de borrar
- [ ] Eliminar `/borrar <id>` — reemplazado por botones desde la lista

**Deps nuevas:**
- [ ] `pip install python-dotenv dateparser` (ya en `pyproject.toml`)

### F7c — Tests del bot (pendiente)
- [ ] `tests/unit/test_api_client.py`
- [ ] `tests/integration/test_bot_handlers.py`

---

## ⏳ FASE 8 — Ollama IA local

**Hardware:** GTX 1060 6GB VRAM + 16GB RAM + CUDA  
**Modelo:** `mistral-nemo:12b` o `qwen2.5-coder:7b`

- [ ] Activar CUDA en WSL2
- [ ] `src/ai/ollama_client.py`
- [ ] Extraer NLP engine de thea-ia
- [ ] `/pregunta <texto>` en el bot

---

## ⏳ FASES 9–11

- **Fase 9** — OpenClaw + agentes IA (orquestador de thea-ia)
- **Fase 10** — CI/CD + Docker + Deploy (Compose: `api` + `bot` + `ollama`)
- **Fase 11** — SQLAlchemy + Alembic (migración desde JSON a SQLite)

---

## ⏳ FASE 12 — Personal Data Platform — sync YAML → SQLite

**Objetivo:** Convertir thdora en el motor del **ecosistema PDP** de Álvaro.  
**Dependencias:** Fase 11 (SQLAlchemy) + Fase 7 (Bot)  
**Docs completos:** [docs/PERSONAL-DATA-PLATFORM.md](docs/PERSONAL-DATA-PLATFORM.md)

### El ecosistema completo

```
repo personal/              ← YAML diarios (fuente de verdad humana)
    └── YYYY-MM-DD.yaml        ← ~2 min cada noche
            ↓
    parse_tracking.py        ← valida schema + calcula nota
            ↓
    SQLite (thdora)          ← datos estructurados, consultas rápidas
            ↓
    thdora FastAPI           ← GET /tracking/semana/13
            ↓
    Bot Telegram             ← /stats /nota-hoy /racha
            ↓
    Ollama/Groq (Fase 8)     ← contexto personal privado
```

### YAML diario (fuente de verdad)

```yaml
fecha: 2026-03-27
dormir_hora: "00:22"
despertar_hora: "09:30"
horas_sueno: 9.1
estudio_m5_horas: 2.0
proyecto_horas: 1.5
aprendizaje_ia_horas: 1.0
ejercicio: true
ejercicio_minutos: 20
thea_horas: 3.0
tabaco: 1
thc: 2
cocaina: false
dias_sin_cocaina: 23
nota: 7.5
notas: "Tarde productiva. Sistema YAML implementado."
```

### Tareas F12
- [ ] `src/tracking/models.py` — modelo SQLAlchemy `DailyRecord`
- [ ] `src/tracking/sync.py` — lee YAML vía GitHub API o ruta local
- [ ] `src/tracking/parser.py` — valida y transforma YAML → `DailyRecord`
- [ ] `GET /tracking/semana/{num}` — métricas automáticas de una semana
- [ ] `GET /tracking/mes/{num}` — métricas de un mes
- [ ] Tests unitarios del parser y sync

**Semana estimada:** S14

---

## ⏳ FASE 13 — Bot tracking — /stats /nota-hoy /racha + alertas

**Objetivo:** El bot responde preguntas de tracking y manda alertas proactivas.  
**Dependencias:** Fase 7 (Bot) + Fase 12 (PDP)

### Comandos nuevos
- [ ] `/stats` — resumen semanal (notas, estudio, sueño, sustancias)
- [ ] `/nota-hoy` — calcula nota del día automáticamente
- [ ] `/racha` — rachas activas (días sin cocaína, ejercicio consecutivo, etc.)

### Alertas automáticas (scheduler)
- [ ] "Llevas 3 días sin ejercicio ⚠️"
- [ ] "Ayer dormiste menos de 5h 😴"
- [ ] "Esta semana vas bien en estudio 📚 +2h respecto S anterior"
- [ ] Recordatorio nocturno: "Rellena el YAML de hoy"

**Semana estimada:** S15

---

_Actualizado: 27 marzo 2026 21:12 CET — F7 al 60%, F7b en desarrollo, PDP alineado_
