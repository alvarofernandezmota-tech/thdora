# THDORA — Contexto para LLMs

> Lee este archivo. Luego lee los archivos que necesites vía los raw links de `llms.txt`.
> Idioma de trabajo: **español siempre**.

---

## Stack

- Python 3.11 · python-telegram-bot v20+ · FastAPI · SQLite · httpx async
- pydantic-settings · APScheduler · Groq (`llama-3.3-70b-versatile`) · Ollama (local, Madre)
- GitHub Contents API (diario en [yggdrasil-dew](https://github.com/alvarofernandezmota-tech/yggdrasil-dew))
- Docker (2 contenedores: `api` + `bot`) sobre servidor Arch Linux **Madre**

---

## Estructura clave

```
src/
├── config.py                        # Todas las variables de entorno (pydantic-settings)
├── bot/
│   ├── main.py                        # Entrypoint bot v4.5 — registra todos los handlers
│   ├── groq_router.py                 # NLP: intent + function calling + transcribe()
│   ├── llm_factory.py                 # ✅ NUEVO: get_router() → GroqRouter | OllamaRouter
│   ├── ollama_router.py               # ✅ NUEVO: OllamaRouter misma interfaz que GroqRouter
│   ├── http_client.py                 # Singleton httpx compartido
│   ├── api_client.py                  # Cliente FastAPI interna
│   ├── middleware.py                  # @require_allowed_user
│   ├── scheduler.py                   # APScheduler — resumen diario + avisos
│   └── handlers/
│       ├── nlp.py                     # Texto libre → get_router() + nlp_history
│       ├── voice.py                   # ✅ NUEVO: notas de voz → Whisper → nlp_handler
│       ├── diario.py                  # /diario → yggdrasil-dew
│       ├── citas.py                   # /nueva, editar, borrar citas
│       ├── habitos.py                 # /habito, registrar hábitos
│       ├── onboarding.py              # /start, /onboarding
│       ├── stats.py                   # /stats + resumen semanal Groq
│       ├── nlp_disambig.py            # Desambiguación NLP inline
│       └── config.py (handler)        # /config
└── services/
    └── github_client.py               # GitHub Contents API — append_to_diario()
.github/
└── workflows/
    └── deploy.yml                     # ✅ NUEVO: CD automático push→main→Madre SSH
```

---

## Estado actual — v0.18.0 (17 jun 2026)

✅ **En producción en Madre** desde 14 jun 2026.

### Funciona hoy
- 10 comandos: `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar` `/diario` `/stats`
- NLP texto libre → get_router() → function calling (crear/consultar/borrar citas)
- Notas de voz → Whisper (Groq) → flujo NLP
- `/diario` guarda entradas en yggdrasil-dew vía GitHub Contents API
- Scheduler: resumen diario + evening log + avisos de citas
- Persistencia SQLite + PicklePersistence (contexto NLP sobrevive reinicios)
- Control de acceso `@require_allowed_user` en todos los handlers sensibles
- LLM switchable: `LLM_BACKEND=groq` (default) o `LLM_BACKEND=ollama`
- CD automático vía GitHub Actions → Madre por SSH

### Sprint 3 — mergeado 17 jun 2026
- `voice.py`: notas de voz con Whisper, reutiliza flujo NLP
- `llm_factory.py`: `get_router()` devuelve GroqRouter u OllamaRouter según `.env`
- `ollama_router.py`: OllamaRouter con misma interfaz que GroqRouter
- `deploy.yml`: CD automático push→main→SSH→Madre, notifica Telegram si falla

### Pendiente Sprint 3 (archivos modificados — no subidos aún)
- `conversation_timeout=300` en: citas.py, habitos.py, onboarding.py, config.py
- `docker-compose.yml`: healthcheck con pgrep
- `groq_router.py`: `process()` acepta `history: list[dict] | None = None`
- `nlp.py`: gestiona `nlp_history` + usa `get_router()`
- `stats.py`: `build_weekly_summary()` + resumen semanal en stats_handler
- `main.py`: registra `voice_handler` antes del handler de texto libre

---

## Plan de Sprints

### Sprint 4 — Estabilización + API tiempo (v0.18.0 → v0.19.0)
1. Smoke test end-to-end en producción: voz, historial NLP, CD → `TESTS.md`
2. Integrar OpenWeatherMap: `/tiempo` + slot NLP → `weather.py`, `nlp.py`, `config.py`
3. `llm_factory`: fallback automático Ollama→Groq si Ollama no responde en >3s
4. Vista semana navegable en `/citas` (Bloque 2) → `citas.py`, `keyboards.py`
5. Limpieza docs: fusionar carpetas, mover archivos huérfanos
6. `stats.py`: gráfico ASCII semanal en resumen Groq
7. Alerta scheduler si Ollama caído al arrancar → `scheduler.py`, `llm_factory.py`

### Sprint 5 — Multiusuario + Tailscale (v0.19.0 → v0.20.0)
1. `user_id` Telegram en todos los modelos SQLite y endpoints FastAPI + Alembic
2. Middleware `@require_allowed_user` desde DB (tabla `allowed_users`)
3. Tailscale en Madre + `scripts/auto_update.sh` cron diario
4. Test aislamiento multiusuario en producción con cuenta beta → `TESTS.md`
5. Secrets GitHub Actions: OWM_API_KEY + GROQ_API_KEY en `deploy.yml`
6. `/diario` end-to-end en Madre con GITHUB_TOKEN de producción
7. Capa regex NLP nivel 0 antes de Ollama/Groq → `nlp.py`, `llm_factory.py`

### Sprint 6 — Plantilla base de agentes + beta cerrada (v0.20.0 → v1.0.0-template)
1. Extraer core reutilizable: `thdora-base` como módulo Python separado
2. Agente gastos: esqueleto sobre `thdora-base` → `agents/gastos/`
3. Suite tests mínima: 10 tests críticos con pytest → `tests/`
4. Beta cerrada: onboarding de 2 usuarios externos + `docs/onboarding.md`
5. Capa Ollama 3b para NLP de bajo coste (qwen2.5:3b o gemma3:4b)
6. Esqueleto Bego Bot sobre `thdora-base` (repo separado)
7. Stress test producción: 50 mensajes en ráfaga → `scripts/stress_test.py`

---

## Reglas de trabajo

1. **Leer antes de tocar** — siempre fetch del raw actual antes de modificar un archivo
2. **Archivo completo** — nunca entregar diffs, siempre el archivo entero
3. **Sin inventar** — si no tienes el archivo, pídelo antes de escribir código
4. **Rama activa**: `main`
5. **Idioma**: español siempre
6. **LLM_BACKEND**: variable en `.env` — `groq` (default producción) | `ollama` (Madre local)

---

> Repo: https://github.com/alvarofernandezmota-tech/thdora
> ROADMAP completo: https://raw.githubusercontent.com/alvarofernandezmota-tech/thdora/main/ROADMAP.md
> Última actualización: 17 jun 2026 — 03:43 CEST — v0.18.0 — Sprint 3 parcial + plan S4/5/6
