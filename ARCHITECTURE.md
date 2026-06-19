# THDORA — Arquitectura del Sistema
_Última actualización: v0.17.0 (2026-06-20)_

## Visión General

THDORA es un asistente personal basado en Telegram que combina un **bot PTB** (Python Telegram Bot v20+) con una **API REST FastAPI** como backend. Los datos se persisten en **SQLite** (dev) o **PostgreSQL** (prod). La comunicación bot↔API es HTTP interna dentro de la red Docker.

```
┌──────────────────────────────────────────────────────────┐
│                    THDORA ECOSYSTEM                        │
└──────────────────────────────────────────────────────────┘

  [Telegram App]
       │ HTTPS (polling)
       ▼
  [═══════════ BOT SERVICE ═══════════]
  │  src/bot/main.py                    │
  │  src/bot/handlers/                  │
  │    ├─ citas.py     (citas + nueva)  │
  │    ├─ habitos.py   (log + editar)   │
  │    ├─ config.py   (hab + notif)     │
  │    ├─ nlp.py       (texto libre)    │
  │    ├─ diario.py   (notas diarias)   │
  │    ├─ stats.py    (estadísticas)    │
  │    └─ onboarding.py                  │
  │  src/bot/api_client.py (httpx)       │
  │  src/bot/scheduler.py (APScheduler) │
  [══════════════════════════════════]
       │ HTTP interno (Docker network)
       ▼
  [═══════════ API SERVICE ═══════════]
  │  src/api/main.py (FastAPI)           │
  │  src/api/routers/                   │
  │    ├─ appointments.py               │
  │    ├─ habits.py                     │
  │    ├─ habit_config.py               │
  │    ├─ user_config.py                │
  │    ├─ summary.py                    │
  │    └─ conversations.py              │
  │  src/db/models.py (SQLAlchemy)      │
  │  alembic/ (migraciones)             │
  [══════════════════════════════════]
       │
       ▼
  [═════════════ DB ══════════════]
  │  SQLite (dev: data/thdora.db)       │
  │  PostgreSQL (prod)                  │
  [══════════════════════════════════]
```

## Capas del Sistema

### 1. Presentación (Bot)

**PTB ApplicationBuilder** registra handlers en orden de prioridad:
1. `ConversationHandler`s (mayor prioridad): `nueva`, `habito`, `edit_apt`, `edit_hab`, `config`, `onboarding`
2. `CallbackQueryHandler`s: navegación, acciones inline (borrar, etc.)
3. `MessageHandler` de texto libre → router `_route_free_text` → acumulación o NLP
4. `CommandHandler`s: `/start`, `/citas`, `/habitos`, `/semana`, `/resumen`, `/cancelar`, `/diario`, `/stats`, `/tiempo`

**Regla de oro**: Cada handler que muestra datos de un usuario **siempre** pasa `user_id = update.effective_user.id` o `query.from_user.id` a `ThdoraApiClient`. Nunca se asume el user_id desde estado interno.

### 2. Cliente HTTP (api_client.py)

`ThdoraApiClient` usa un patrón **singleton con cliente compartido** (`httpx.AsyncClient`):
- Se crea lazy en el primer `_ensure_client()`
- Todas las llamadas pasan `user_id` como query param `?user_id=X`
- `_validate_user_id()` lanza `ValueError` si `user_id <= 0` antes de hacer la request
- El cliente se cierra limpiamente en `_post_shutdown` del bot

### 3. API REST (FastAPI)

Cada router expone endpoints RESTful con `user_id` como query param obligatorio:
- `GET /habits/{fecha}?user_id=X`
- `POST /habits/{fecha}?user_id=X` body: `{habit, value}`
- `GET /appointments/{fecha}?user_id=X`
- `POST /appointments/{fecha}?user_id=X` body: `{name, time, type, notes}`
- `GET /habit-config/?user_id=X`
- `PUT /user_config/{user_id}?user_id=X` body: dict parcial

El endpoint `/health/live` devuelve `200 OK` sin autenticación (usado por Docker healthcheck).

### 4. Persistencia (SQLAlchemy + Alembic)

Modelos principales:
- `HabitLog`: `(user_id, date, habit, value)` — unique por `(user_id, date, habit)`
- `Appointment`: `(user_id, date, index, name, time, type, notes)`
- `HabitConfig`: `(user_id, name, habit_type, unit, quick_vals)`
- `UserConfig`: `(user_id, daily_summary_enabled, notif_time, ...)` — one per user
- `Conversation`: `(user_id, session_id, role, content, timestamp)`

Alembic gestiona todas las migraciones. El entrypoint Docker ejecuta `alembic upgrade head` antes de arrancar uvicorn.

## Flujo de Datos — Ejemplo: registrar hábito

```
Usuario escribe "Agua" en Telegram
  ↓
PTB routing: ConversationHandler "nuevo_habito" (estado HABITO_NOMBRE)
  ↓
habito_recv_nombre_text() → guarda nombre en user_data
  ↓
_ask_habito_value() → llama api.get_habit_config(nombre, user_id)
  ↓
ThdoraApiClient._request("GET", "/habit-config/Agua", user_id=123)
  ↓
FastAPI GET /habit-config/Agua?user_id=123
  ↓
SQLAlchemy: SELECT * FROM habit_config WHERE user_id=123 AND name='Agua'
  ↓
respuesta: None (no configurado) → teclado genérico
  ↓
Usuario escribe "2L"
  ↓
habito_recv_value_text() → _save_habito()
  ↓
api.log_habit(date_str, "Agua", "2L", 123)
  ↓
FastAPI POST /habits/2026-06-20?user_id=123 body={habit:"Agua", value:"2L"}
  ↓
SQLAlchemy: INSERT/UPDATE habit_log
  ↓
✅ Bot responde: "Hábito registrado: Agua 2L"
```

## Decisiones Técnicas Clave

Ver `docs/ADR-001-api-client-singleton.md` y `docs/ADR-002-user-id-obligatorio.md`.

| Decisión | Razón |
|---|---|
| Bot y API en servicios Docker separados | Pueden escalar y reiniciarse independientemente |
| `httpx.AsyncClient` singleton | Evita abrir socket por request; reutiliza conexiones keep-alive |
| `user_id` en cada llamada API (no JWT) | Simplicidad para bot single-user; sin overhead de auth |
| SQLite en dev, Postgres en prod | SQLite = zero-config local; Postgres = concurrencia real |
| PTB PicklePersistence | Estado de conversación persiste entre reinicios del bot |
| APScheduler en proceso del bot | Evita servicio extra; scheduler jobs = callbacks async de PTB |

## Estructura de Directorios

```
thdora/
├── src/
│   ├── bot/
│   │   ├── handlers/       # Un archivo por dominio (citas, habitos, config...)
│   │   ├── utils/          # Funciones puras reutilizables (accum, dates)
│   │   ├── api_client.py   # Único punto de acceso a la API REST
│   │   ├── keyboards.py    # Todos los InlineKeyboardMarkup del bot
│   │   ├── scheduler.py    # APScheduler jobs (reminders, resumen diario)
│   │   └── main.py         # ApplicationBuilder + registro de handlers
│   ├── api/
│   │   ├── routers/        # Un router FastAPI por recurso
│   │   └── main.py         # FastAPI app + middleware
│   ├── db/
│   │   ├── models.py       # SQLAlchemy ORM models
│   │   └── session.py      # get_db() dependency
│   └── config.py           # Settings Pydantic desde .env
├── alembic/                # Migraciones de BD
├── tests/                  # pytest + AsyncMock suite
├── scripts/
│   └── autotest.py         # Verificación de ecosistema sin pytest
├── docker/
│   └── entrypoint.sh       # alembic + uvicorn | python bot
├── docs/                   # ADRs y documentación técnica
├── Dockerfile              # Multi-stage builder+runtime
├── docker-compose.yml      # api + bot + (opcional) grafana
├── ARCHITECTURE.md         # Este archivo
├── CHANGELOG.md            # Historial de versiones
├── CONTRIBUTING.md         # Guía para contribuir
├── PLAN_MANANA.md          # Estado actual + pasos de lanzamiento
└── llms.txt                # Resumen compacto para LLMs
```

## Patrones y Convenciones

### Handlers PTB
- Cada `ConversationHandler` tiene su factory `build_X_handler()` en su módulo
- El `user_id` se guarda en `context.user_data["X_user_id"]` en el entry point y se reutiliza en todos los pasos
- Los fallbacks usan `/cancelar` que llama a `context.user_data.clear()` + `ConversationHandler.END`

### API Client
- Nunca llamar métodos de `ThdoraApiClient` con `user_id=0` o sin `user_id`
- Siempre capturar `ApiError` en los handlers (no dejar propagar)
- Usar `asyncio.wait_for(coro, timeout=5.0)` para llamadas que pueden colgar

### Tests
- Mock de `api` a nivel de módulo: `patch("src.bot.handlers.X.api", mock_api)`
- No usar `@pytest.mark.asyncio` individualmente; configurar `asyncio_mode=auto` en `pytest.ini`
- Los fixtures de `conftest.py` son la única fuente de mocks compartidos
