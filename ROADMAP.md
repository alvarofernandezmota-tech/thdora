# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.11.0 (13 abril 2026)

```
Bot Telegram (9 comandos + 5 ConversationHandlers + inline buttons)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
```

### Lo que funciona hoy
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar`
- Saludo contextual (buenos días/tardes/noches)
- Navegación ◀️▶️ con fecha real visible en botón central
- Vista detalle de cita con click en ⏰ hora
- Inline buttons: borrar/editar/sumar citas y hábitos
- Editar nombre y valor de hábito
- Nombre de hábito libre (sin lista predefinida)
- Conflicto hora en citas: aviso ⚠️ al crear
- Conflicto hábito existente: Sobreescribir / Sumar / Cancelar
- Cambio de vista Citas ↔ Hábitos desde la nav
- `/semana` con navegación semanal y botones por día
- `/config` para configurar tipos de hábitos con botones rápidos
- Fechas flexibles: `hoy`, `mañana`, `ayer`, `27/03`, nombres de día
- **Datos persistentes en SQLite** — sobreviven a reinicios
- **Franjas horarias en /nueva** — 🌅 Mañana / 🌆 Tarde / 🌙 Noche + hora en punto + cuartos
- **Código modular** — `src/bot/handlers/` package (6 módulos) + `keyboards.py` + `utils/`
- **➕ Nueva cita desde botón del menú** — arranca ConversationHandler directamente ✅
- **➕ Nuevo hábito desde botón del menú** — arranca ConversationHandler directamente ✅
- **Menú operativo al 100%** — probado en vivo ✅

---

## ✅ Completadas

### F1–F5 — Base, abstracción, core
- `AbstractLifeManager`, `MemoryLifeManager`, `JsonLifeManager`
- Arquitectura limpia con ADRs

### F6 — FastAPI REST
- Endpoints CRUD para citas y hábitos
- `GET /summary/{date}`

### F7 — Bot Telegram v1+v2
- 5 comandos + `/nueva` 5 pasos + inline buttons
- Fechas flexibles con `dateparser`
- Acumulación `+N` en hábitos

### F8 — Endpoints temporales
- `GET /appointments/week/{date}`, range, upcoming
- `GET /habits/week/{date}`, range, stats
- `GET /summary/week/{date}`

### F9 — Persistencia SQLite ✅
- `SQLiteLifeManager` CRUD completo
- `data/thdora.db` — persistencia real

### F9.1 — Routers SQLite ✅
### F9.2 — Fixes v2.1 ✅
### F9.3 — UI unificada ✅
### F9.4 — Vista detalle cita ✅
### F9.5 — UX avanzada bot ✅ (franjas horarias incluidas)
### F9.6 — Refactor bot (handlers modular) ✅

```
src/bot/
├── main.py
├── api_client.py
├── keyboards.py
├── utils/
│   ├── dates.py
│   └── accum.py
└── handlers/
    ├── __init__.py
    ├── menu.py
    ├── citas.py           ← franjas horarias + entry point botón
    ├── habitos.py         ← entry point botón
    ├── semana.py
    ├── config.py
    └── common.py
```

### F9.7 — Pruebas en vivo + fix entry points ✅ (13 abril 2026)

> Todas las funciones del bot probadas en Telegram real.

- [x] Flujo `/nueva` con franjas horarias — **funciona** ✅
- [x] Navegación citas/hábitos con ◀️▶️ — **funciona** ✅
- [x] Editar/borrar cita — **funciona** ✅
- [x] Editar/borrar/sumar hábito — **funciona** ✅
- [x] `/semana` — **funciona** ✅
- [x] ➕ Nueva cita desde botón menú — **funciona** ✅ (fix entry point)
- [x] ➕ Nuevo hábito desde botón menú — **funciona** ✅ (fix entry point)
- [x] Crear hábito contra API (POST `/habits/`) — **201 Created** ✅
- [x] Crear cita contra API (POST `/appointments/`) — **201 Created** ✅
- [x] Borrar cita (DELETE `/appointments/`) — **204 No Content** ✅

### F9.8 — Documentación técnica completa ✅ (13 abril 2026)

> Todo el sistema documentado antes de implementar F12.

- [x] `docs/FLUJOS_DETALLADOS.md` — todos los flujos del bot con estados y casos borde
- [x] `docs/API_REFERENCE.md` — referencia completa de los 14 endpoints
- [x] `docs/CONVENCIONES.md` — patrones, variables de entorno, orden de handlers
- [x] `docs/INDEX.md` — mapa de lectura por rol
- [x] `docs/F12_NOTIFICACIONES_DESIGN.md` — diseño completo con extensiones futuras

---

## 🔶 En curso / Próximo — v0.12.x

### F12 — Notificaciones proactivas 🔜 SIGUIENTE

> Diseño completo en [docs/F12_NOTIFICACIONES_DESIGN.md](docs/F12_NOTIFICACIONES_DESIGN.md)

**V1 — a implementar:**
- [ ] `src/db/models.py` — tabla `UserConfig` (defaults automáticos)
- [ ] `src/core/impl/sqlite_lifemanager.py` — `get_user_config`, `upsert_user_config`
- [ ] `src/api/routers/user_config.py` — `GET` + `PUT /user_config/{user_id}`
- [ ] `src/api/main.py` — registrar router
- [ ] `src/bot/api_client.py` — `get_user_config()`, `update_user_config()`
- [ ] `src/bot/keyboards.py` — teclados menú config + notificaciones
- [ ] `src/bot/handlers/config.py` — rediseño con `CFG_MENU` raíz + rama notificaciones
- [ ] `src/bot/scheduler.py` — APScheduler: resumen diario + evening log + jobs por cita
- [ ] `src/bot/handlers/citas.py` — reprogramar jobs al crear/editar/borrar
- [ ] `src/bot/main.py` — `start_scheduler(app)` al arrancar

**V1.1 — extensiones apuntadas (más adelante):**
- [ ] Snooze `[⏰ +15min]` en avisos
- [ ] Silencio nocturno (23:00–07:00 configurable)
- [ ] Cita inminente (aviso si creas cita con <2h de margen)

**V1.2 — extensiones apuntadas:**
- [ ] Resumen semanal (lunes 08:00)
- [ ] Recordatorio por hábito específico
- [ ] Notificación de racha 🔥

---

### F10 — Docker + despliegue 24/7 🔜

> **Objetivo:** THDORA corriendo siempre en un servidor, sin intervención manual

```yaml
# docker-compose.yml
services:
  api:
    build: .
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    volumes: ["./data:/app/data"]
    ports: ["8000:8000"]
  bot:
    build: .
    command: python -m src.bot.main
    depends_on: [api]
    env_file: .env
```

**Tareas:**
- [ ] `Dockerfile` — imagen base Python 3.12, deps instaladas
- [ ] `docker-compose.yml` — servicios `api` + `bot` + volumen `data/`
- [ ] Health checks y reinicio automático
- [ ] Variables de entorno seguras (`.env` + secrets)
- [ ] Probar en VPS (Railway / DigitalOcean / Raspberry Pi)
- [ ] Backup automático de `thdora.db`

---

### F11 — Multi-usuario 🔜

- [ ] Añadir `user_id` a todas las tablas SQLite
- [ ] Middleware en API para `X-User-Id`
- [ ] Bot envía `user_id` en cada llamada a la API
- [ ] Onboarding: primer `/start` → configura perfil

> ⚠️ `user_id` ya está pre-modelado en `UserConfig` (F12). Facilita la migración.

---

### F13 — IA conversacional 🔜

- [ ] `src/core/ai/` — provider abstracto (Groq / OpenAI / Claude / Ollama)
- [ ] `src/core/ai/intent_parser.py` — extrae intención + entidades
- [ ] `/ia` — modo conversación libre
- [ ] Soporte mensajes de voz (Whisper)

---

### F14 — Módulo Tracking personal 🔜

> sueño, sustancias, estado, estudio, proyecto

- [ ] `src/db/models.py` — tabla `daily_tracking`
- [ ] `src/api/routers/tracking.py` — endpoints CRUD
- [ ] `src/bot/handlers/tracking.py` — formulario guiado
- [ ] Sistema de puntuación diaria (0–10)
- [ ] Dashboard tracking — tendencias + racha

---

### F15 — Gamificación RPG 🔜
- XP por hábitos cumplidos (campo `xp_rule` ya modelado en `HabitConfig`)
- Niveles: 🐣 Novato → 👑 Leyenda
- Rachas diarias + misiones
- Conecta con notif de racha de F12.v1.2

### F16 — Telegram Mini App 🔜
- HTML5/React + `Telegram.WebApp` SDK
- Conectar con API FastAPI existente

### F17 — PWA 🔜
- App instalable en móvil, offline-first

### F18 — React Native 🔜

---

## Orden recomendado de implementación

```
F12 (Notificaciones) → F10 (Docker 24/7) → F11 (Multi-usuario)
    → F13 (IA) → F14 (Tracking) → F15 (Gamificación)
    → F16/F17/F18 (Apps)
```

> F12 primero porque da valor inmediato al usuario actual.
> F10 justo después para que el scheduler corra 24/7 en un servidor real.
> F11 antes de F13+ para no tener que hacer dos migraciones.

---

_Última actualización: 13 abril 2026 — 21:24 CEST_
