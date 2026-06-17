# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [CONTEXT.md](CONTEXT.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.19.0 (17 junio 2026)

```
Bot Telegram (11 comandos + voz + 5 ConversationHandlers + NLP texto libre)
    ↕ httpx async (singleton)
get_router() → GroqRouter | OllamaRouter (con fallback automático >3s)
    ↕ Groq API (NLP + Whisper) / Ollama local (Madre)
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST (14 endpoints)
SQLite (data/thdora.db)
Scheduler APScheduler (resumen diario + avisos citas + alerta Ollama caído)
CD automático: GitHub Actions → SSH → Madre
```

🟢 **En producción** en servidor **Madre** (Omarchy, Arch Linux) con Docker desde 14 junio 2026.

### Lo que funciona hoy ✅
- 11 comandos: `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar` `/diario` `/stats` `/tiempo`
- Notas de voz → Whisper (Groq) → flujo NLP
- NLP con historial conversacional real (`nlp_history` → Groq)
- LLM switchable: `groq` (producción) | `ollama` (Madre local) con fallback automático
- CD automático GitHub Actions → Madre por SSH
- Scheduler: alerta Telegram si Ollama caído al arrancar
- `/tiempo [ciudad]` vía OpenWeatherMap
- `conversation_timeout=300` en todos los ConversationHandlers
- Persistencia SQLite + PicklePersistence (contexto NLP sobrevive reinicios)

---

## ✅ Sprints completados

### Sprint 1 — /diario + pydantic-settings (v0.17.0) ✅
- `src/config.py` pydantic-settings + GITHUB_TOKEN
- `src/services/github_client.py` GitHub Contents API
- `src/bot/handlers/diario.py` + registrar /diario

### Sprint 2 — NLP + infraestructura base (v0.17.0) ✅
- httpx singleton + connection pooling
- `@lru_cache` en build_system_prompt + 256 tokens
- `@require_allowed_user` reutilizable
- TYPING + filtro mensajes triviales
- PicklePersistence `update_interval=60`

### Sprint 3 — Voz + historial + CD (v0.18.0) ✅
- `voice.py`: notas de voz con Whisper
- `llm_factory.py` + `ollama_router.py`: arquitectura LLM switchable
- `groq_router.py`: `process()` acepta `history: list[dict]`
- `nlp.py`: `nlp_history` gestionado en persistence
- `deploy.yml`: CD automático push→main→SSH→Madre
- `conversation_timeout=300` en todos los handlers
- `docker-compose.yml`: healthcheck con `pgrep`

### Sprint 4 — Estabilización + API tiempo (v0.19.0) ✅ PARCIAL
- `llm_factory.py`: fallback automático Ollama→Groq si >3s o error
- `weather.py`: `/tiempo [ciudad]` vía OpenWeatherMap
- `src/config.py`: `OWM_API_KEY: str = ""`
- `scheduler.py`: alerta Ollama caído al arrancar → mensaje privado al owner

**Pendiente Sprint 4:**
- [ ] Smoke test end-to-end en producción (voz, historial, CD) → `TESTS.md`
- [ ] Registrar `/tiempo` en `main.py`
- [ ] Vista semana navegable en `/citas` → `citas.py`, `keyboards.py`
- [ ] Limpieza docs: fusionar carpetas huérfanas
- [ ] Gráfico ASCII semanal en `stats.py`

---

## 🟠 Sprint 5 — Multiusuario + Tailscale (v0.19.0 → v0.20.0)

| # | Tarea | Archivo(s) | Criterio de hecho | Prioridad |
|---|-------|------------|-------------------|-----------|
| 1 | `user_id` Telegram en todos los modelos SQLite y endpoints FastAPI | `models.py`, `api/`, `alembic/` | Migración Alembic; cada endpoint filtra por `user_id`; tests pasan | 🔴 crítica |
| 2 | Middleware `@require_allowed_user` desde DB en vez de `.env` | `middleware.py`, `models.py` | Tabla `allowed_users`; `/admin_add_user`; recarga sin reiniciar | 🔴 alta |
| 3 | Tailscale en Madre + `scripts/auto_update.sh` cron diario | `scripts/` | Madre accesible vía Tailscale; cron `git pull + docker compose up -d` | 🔴 alta |
| 4 | Test aislamiento multiusuario con cuenta beta | `TESTS.md` | Usuario beta; datos no se mezclan con admin | 🔴 alta |
| 5 | Secrets GitHub Actions: OWM_API_KEY + GROQ_API_KEY | `deploy.yml` | CD inyecta secrets como env vars; verificado en pipeline | 🟡 media |
| 6 | `/diario` end-to-end en Madre con GITHUB_TOKEN producción | `diary.py`, `deploy.yml` | Commit real desde Madre en yggdrasil-dew | 🟡 media |
| 7 | Capa regex NLP nivel 0 antes de Ollama/Groq | `nlp.py`, `llm_factory.py` | Intenciones simples ≤200ms sin LLM | 🟡 media |

---

## 🔵 Sprint 6 — Plantilla base de agentes + beta cerrada (v0.20.0 → v1.0.0-template)

| # | Tarea | Archivo(s) | Criterio de hecho | Prioridad |
|---|-------|------------|-------------------|-----------|
| 1 | Extraer core reutilizable: `thdora-base` módulo Python | `thdora_base/`, `pyproject.toml` | Importable desde proyecto externo; README en 5 pasos | 🔴 crítica |
| 2 | Agente gastos: esqueleto sobre `thdora-base` | `agents/gastos/` | `/gasto` + `/resumen_gastos`; usa `llm_factory` sin duplicar | 🔴 alta |
| 3 | Suite tests mínima: 10 tests críticos con pytest | `tests/` | `pytest -v` al 100% local + CI; cubre fallback LLM, user_id, API | 🔴 alta |
| 4 | Beta cerrada: 2 usuarios externos + `docs/onboarding.md` | `docs/` | 7 días uso real; issues recogidos en GitHub | 🟡 alta |
| 5 | Ollama 3b nivel 1 (qwen2.5:3b o gemma3:4b) | `llm_factory.py`, `ollama_router.py` | `llm_factory` usa nivel 1 para intenciones medias; Groq 70b para síntesis | 🟡 media |
| 6 | Bego Bot repo separado sobre `thdora-base` | repo `bego-bot` | Desplegable en ≤10 min siguiendo README | 🟢 media |
| 7 | Stress test: 50 mensajes en ráfaga | `scripts/stress_test.py` | P95 latencia ≤2s; 0 crashes | 🟢 baja |

---

## 🧠 Investigación: Arquitecturas LLM aplicables a THDORA

> Análisis de cómo las técnicas de chatbots avanzados (2026) se pueden aplicar progresivamente.

### Qué usa THDORA hoy
- Ventana de contexto: `nlp_history` → últimos 10 mensajes inyectados en Groq (128k context)
- LLM: decoder-only Transformer (llama-3.3-70b) vía Groq API
- Arquitectura 3 niveles planificada: regex → Ollama 3b → Groq 70b

### Aplicaciones por prioridad

#### 🔴 Aplicar ya (Sprint 5-6)
| Técnica | Aplicación en THDORA | Esfuerzo |
|---------|---------------------|----------|
| **Arquitectura 3 niveles NLP** | regex (nivel 0) → Ollama 3b (nivel 1) → Groq 70b (nivel 2) | Sprint 5 |
| **Memoria persistente de usuario** | Guardar perfil: nombre, objetivos, preferencias de notificación en SQLite | Sprint 6 |
| **Contexto dinámico (RAG leve)** | Inyectar citas del día + hábitos recientes en cada llamada Groq | Ya parcial |
| **Resumen conversación** | Comprimir `nlp_history` cuando supera 20 mensajes en vez de truncar | Sprint 5 |

#### 🟡 Aplicar en v2.0
| Técnica | Aplicación en THDORA | Esfuerzo |
|---------|---------------------|----------|
| **Tool Use / Function Calling avanzado** | Agentes que ejecutan múltiples herramientas en cadena (crear cita + registrar hábito + guardar diario en un mensaje) | Medio |
| **Memoria semántica (RAG real)** | Base de datos vectorial local (ChromaDB) para recordar entradas del diario y contexto de semanas anteriores | Alto |
| **Resumen automático largo plazo** | Groq genera resumen semanal/mensual que se guarda como memoria comprimida | Medio |
| **Perfil usuario dinámico** | El agente actualiza el perfil del usuario después de cada sesión (ej: detecta que el usuario hace deporte los lunes) | Alto |

#### 🟢 Visión a largo plazo (v3.0+)
| Técnica | Aplicación en THDORA |
|---------|---------------------|
| **Agentic RAG** | THDORA razona, recupera contexto de meses, actúa y actualiza memoria de forma autónoma |
| **MoE local** | Modelo local con expertos especializados: uno para citas, otro para hábitos, otro para diario |
| **Reasoning interno** | Chain-of-thought oculto antes de responder (ya disponible en Groq con DeepSeek-R1) |
| **Memoria continua** | Estado interno que persiste entre sesiones sin necesidad de inyectar historial |

### Conclusión de la investigación
THDORA ya implementa la base correcta. El camino natural es:
1. **Ahora**: regex NLP + compresión historial inteligente
2. **v2.0**: RAG con ChromaDB local + perfil dinámico de usuario
3. **v3.0**: Agente autónomo con memoria continua y razonamiento profundo

---

## 🧪 Checklist de pruebas en producción

| Test | Versión | Estado |
|------|---------|--------|
| Voz → transcripción → NLP | Sprint 3 | 🔲 Pendiente |
| Historial NLP real (nlp_history) | Sprint 3 | 🔲 Pendiente |
| CD automático push→Madre | Sprint 3 | 🔲 Pendiente |
| Fallback Ollama→Groq >3s | Sprint 4 | 🔲 Pendiente |
| /tiempo [ciudad] | Sprint 4 | 🔲 Pendiente |
| Alerta Ollama caído al arrancar | Sprint 4 | 🔲 Pendiente |
| Multiusuario aislamiento user_id | Sprint 5 | 🔲 Pendiente |
| /diario end-to-end en producción | Sprint 5 | 🔲 Pendiente |

---

## 🤖 Visión — Plataforma de Agentes Personales

```
Docker + FastAPI + SQLite + Bot Telegram + Groq/Ollama NLP
         ↑
   thdora-base (módulo reutilizable)
   Cambias solo: system prompt + endpoints API + handlers bot
```

| Agente | Propósito | Estado |
|--------|-----------|--------|
| **THDORA** | Citas, hábitos, salud | 🟢 Producción |
| Agente gastos | Tickets, presupuesto mensual | 🔲 Sprint 6 |
| Bego Bot | Asistente personalizado | 🔲 Sprint 6 |
| Agente estudio | Flashcards, progreso | 🔲 v2.0 |
| Agente trabajo | Tareas, deadlines | 🔲 v2.0 |

---

_Última actualización: 17 jun 2026 — 04:00 CEST — v0.19.0 — Sprint 3+4 completados + investigación LLM_
