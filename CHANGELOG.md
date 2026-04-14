# 📋 THDORA — CHANGELOG

> **Navegación rápida:** [README](README.md) · [ROADMAP](ROADMAP.md) · [Índice docs](docs/INDEX.md)

---

## [v0.12.0] — 14 abril 2026

### ✨ Añadido — NLP con Groq (F13-base)

- **`src/bot/groq_router.py`** — Orquestador NLP completo:
  - `classify_intent()` con `llama-3.1-8b-instant` (~50ms)
  - `extract_cita()` con `llama-3.3-70b-versatile` → JSON estructurado
  - `extract_habito()` con `llama-3.3-70b-versatile` → JSON estructurado
  - `chat_response()` con `llama-3.3-70b-versatile` → respuesta libre
  - `route()` — orquestador principal con historial de 10 mensajes
  - Memoria conversacional en `context.user_data["nlp_history"]`

- **`src/bot/handlers/nlp.py`** — Handler de Telegram:
  - Detecta conflictos de hora antes de crear cita
  - Formato de respuesta consistente con el resto del bot
  - Fallback a `/nueva` o `/habito` si la extracción falla

- **`src/bot/main.py`** — Actualizado:
  - `_route_free_text()` prioriza `acum_hab_nombre` y cae a NLP
  - Import de `nlp_handler`
  - Documentación de `GROQ_API_KEY` en docstring

- **`docs/NLP_ARQUITECTURA.md`** — Documentación completa:
  - Decisiones de arquitectura multi-modelo
  - Roadmap de proveedores opcionales (OpenRouter, Claude, Gemini)
  - Ejemplos de uso y plan de voz (Whisper)

### 🔧 Requiere para activar
```
GROQ_API_KEY=gsk_xxxx  ← añadir al .env
pip install groq        ← instalar dependencia
```

---

## [v0.11.0] — 13 abril 2026

### ✨ Añadido — F12 Notificaciones + Documentación técnica

- `UserConfig` en SQLite (horarios resumen + evening)
- APScheduler integrado: resumen diario + evening log + jobs one-shot por cita
- `/config` → rama notificaciones con horarios configurables
- Scheduler arranca en `post_init` (sin RuntimeError)
- Fix entry points `/config`: `quick_config` como entry_point del ConversationHandler

### 📚 Documentación
- `docs/FLUJOS_DETALLADOS.md`
- `docs/API_REFERENCE.md`
- `docs/CONVENCIONES.md`
- `docs/INDEX.md`
- `docs/F12_NOTIFICACIONES_DESIGN.md`

---

## [v0.10.0] — Abril 2026

### ✨ Añadido — Bot v4 modular + UX avanzada
- Refactor handlers en package `src/bot/handlers/`
- Franjas horarias en `/nueva`: 🌅 Mañana / 🌆 Tarde / 🌙 Noche
- Entry points desde botones del menú (➕ cita, ➕ hábito)
- Vista detalle de cita al pulsar ⏰ hora
- Editar nombre y valor de hábito inline
- Cambio vista Citas ↔ Hábitos desde la nav
- Conflicto hábito: Sobreescribir / Sumar / Cancelar

---

## [v0.9.0] — Marzo 2026

### ✨ Añadido — Persistencia SQLite
- `SQLiteLifeManager` CRUD completo
- `data/thdora.db` — datos persistentes entre reinicios
- 14 endpoints REST en FastAPI
- `GET /summary/{date}`, `/week`, `/range`, `/stats`

---

## [v0.1–0.8] — Febrero–Marzo 2026

- Arquitectura base (`AbstractLifeManager`, `MemoryLifeManager`, `JsonLifeManager`)
- FastAPI REST con CRUD citas y hábitos
- Bot Telegram v1–v3: comandos, inline buttons, fechas flexibles
- Endpoints temporales (semana, rango, próximas citas)

---

_Última actualización: 14 abril 2026 — 11:46 CEST_
