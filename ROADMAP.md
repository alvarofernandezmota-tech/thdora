# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.8.1 (28 marzo 2026)

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
- Routers migrados a SQLite
- `data/thdora.db` — persistencia real

### F9.1 — Routers SQLite ✅
- Todos los routers usan `SQLiteLifeManager`

### F9.2 — Fixes v2.1 ✅
- Fix bug tipo `/nueva`
- Fix contexto acum suelto
- `_clean_acum_context()` + `_skip_to()` helpers

### F9.3 — UI unificada ✅
- Menú principal con botones
- Navegación ◀️▶️ en citas y hábitos
- Botón 🏠 Menú desde todas las vistas
- Cambio de vista Citas ↔ Hábitos
- Botón ← Volver al día

### F9.4 — Vista detalle cita ✅
- Click en ⏰ hora → vista detalle
- Editar / Borrar desde vista detalle

### F9.5 — UX avanzada bot ✅
- Fix bug semana (lunes mal calculado)
- Fecha real visible en botón central nav: `[Sáb 28 mar]`
- Saludo contextual según hora del día
- Botón ➕ Nueva cita directo desde vista /citas
- Nombre hábito libre (elimina lista hardcodeada)
- Editar nombre del hábito además del valor
- Nuevo hábito desde vista hábitos del día
- Config hábitos: tipo, unidad, botones rápidos
- Conflicto hora citas + conflicto hábito existente

---

## 🔶 Próximo — v0.9.x

### F9.6 — Refactor bot (handlers modular) 🔜 NEXT

> **Objetivo:** dividir `handlers.py` (60KB, ~1500 líneas) en módulos mantenibles

```
src/bot/
├── main.py              ← actualizar imports
├── api_client.py        ← sin cambios
├── utils/
│   ├── dates.py         ← _parse_date_*, _date_label, _date_short, _greeting
│   └── accum.py         ← _accumulate_value, _clean_acum_context
├── keyboards.py         ← todas las funciones _kb_* y _nav_keyboard
└── handlers/
    ├── __init__.py      ← exporta todo
    ├── menu.py          ← cmd_start, cb_menu_home, cb_quick_dispatch
    ├── citas.py         ← cmd_citas, nav, detail, borrar/editar, /nueva
    ├── habitos.py       ← cmd_habitos, nav, /habito, borrar/editar/sumar
    ├── semana.py        ← cmd_semana, cb_semana_nav
    ├── config.py        ← cmd_config, build_config_handler
    └── common.py        ← cmd_cancelar, error_handler
```

**Tareas:**
- [ ] Crear `src/bot/utils/dates.py`
- [ ] Crear `src/bot/utils/accum.py`
- [ ] Crear `src/bot/keyboards.py`
- [ ] Crear `src/bot/handlers/menu.py`
- [ ] Crear `src/bot/handlers/citas.py`
- [ ] Crear `src/bot/handlers/habitos.py`
- [ ] Crear `src/bot/handlers/semana.py`
- [ ] Crear `src/bot/handlers/config.py`
- [ ] Crear `src/bot/handlers/common.py`
- [ ] Actualizar `src/bot/main.py` con nuevos imports
- [ ] Eliminar `src/bot/handlers.py` monolítico

---

### F9.7 — Docker + despliegue 24/7 🔜

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

### F9.8 — Multi-usuario 🔜

> **Objetivo:** el bot funciona para varios usuarios con datos separados

- [ ] Añadir `user_id` a todas las tablas SQLite
- [ ] Middleware en API para `X-User-Id`
- [ ] Bot envía `user_id` en cada llamada a la API
- [ ] Onboarding: primer `/start` → configura perfil

---

### F10 — Módulo Tracking personal 🔜

> **Objetivo:** tracking diario completo — sueño, sustancias, estado, estudio

```yaml
# Ejemplo YAML tracking diario
fecha: 2026-03-28
dormir_hora: "00:22"
despertar_hora: "09:30"
horas_sueno: 9.1
estudio_horas: 2.0
proyecto_horas: 1.5
ejercicio: true
ejercicio_minutos: 20
nota: 7.5
notas: "Tarde productiva."
```

**Tareas:**
- [ ] `src/db/models.py` — tabla `daily_tracking`
- [ ] `src/api/routers/tracking.py` — endpoints CRUD
- [ ] `src/bot/handlers/tracking.py` — formulario guiado
- [ ] Sistema de puntuación diaria (0–10)
- [ ] Dashboard tracking — tendencias + racha

---

### F11 — Notificaciones proactivas 🔜

> **Objetivo:** THDORA te habla primero

- [ ] `src/bot/scheduler.py` — APScheduler
- [ ] Morning check-in (08:00): citas del día
- [ ] Evening log (22:00): registra hábitos del día
- [ ] Alerta −30min antes de cita

---

### F12 — IA conversacional 🔜

> **Objetivo:** entender lenguaje natural en el bot

```
🎤 "Mañana a las diez tengo dentista"
   → ✅ Cita creada: mañana 10:00 — Dentista

🎤 "He dormido siete horas"
   → ✅ sueño: 7h
```

- [ ] `src/core/ai/` — provider abstracto (Groq / OpenAI / Claude / Ollama)
- [ ] `src/core/ai/intent_parser.py` — extrae intención + entidades
- [ ] `/ia` — modo conversación libre
- [ ] Soporte mensajes de voz (Whisper)

---

### F13 — Gamificación RPG 🔜

> **Se activa cuando ya hay semanas de datos reales**

- XP por hábitos cumplidos
- Niveles: 🐣 Novato → 👑 Leyenda
- Rachas diarias + misiones
- `/stats` — nivel, XP, racha

---

### F14 — Telegram Mini App 🔜

> **Objetivo:** interfaz visual completa dentro de Telegram

```
Bot: /start → [📱 Abrir THDORA App]
              ↓
         Mini App React:
         - Calendario drag&drop
         - Dashboard XP + rachas
         - Stats de hábitos
         - Gestión visual de citas
```

- [ ] HTML5/React base + `Telegram.WebApp` SDK
- [ ] BotFather → `/setmenubutton` → URL Mini App
- [ ] Deploy Vercel/Netlify (gratis)
- [ ] Conectar con API FastAPI existente

---

### F15 — PWA (Progressive Web App) 🔜

> **Objetivo:** app instalable en móvil, funciona sin Telegram

- Misma UI que Mini App pero independiente
- Offline-first con service worker
- Notificaciones push nativas

---

### F16 — React Native (futuro) 🔜

> **Solo si el proyecto escala a múltiples usuarios**

- App nativa iOS + Android
- Publicación en App Store + Google Play (~130€/año)
- Usa misma API FastAPI

---

## 📊 Visión general de fases

```
AHORA  →  F9.6  →  F9.7  →  F9.8  →  F10   →  F11
Refactor  Docker   Multi-usr  Tracking  Notifs

F12   →  F13   →  F14      →  F15  →  F16
IA    →  RPG   →  Mini App  →  PWA  →  React Native
```

---

_Última actualización: 28 marzo 2026 — 21:43 CET_
