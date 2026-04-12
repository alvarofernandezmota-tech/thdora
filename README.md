# 🧠 THDORA

> **Tu asistente personal de gestión de vida — Bot Telegram + FastAPI + SQLite + IA (próximamente)**

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135%2B-009688)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57)](https://sqlite.org)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-22%2B-2CA5E0)](https://python-telegram-bot.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📍 ¿Por dónde empiezo?

> **→ Lee [`COMO_PROCEDER.md`](COMO_PROCEDER.md)** — te dice exactamente dónde está el proyecto, cómo arrancarlo y qué probar.

---

## ¿Qué es THDORA?

THDORA es un ecosistema de **gestión personal** que vive en Telegram. Registra citas, hábitos diarios y genera resúmenes — todo desde el móvil, sin abrir ninguna app extra.

Los datos se guardan en **SQLite local** (persisten entre reinicios) y se exponen a través de una **API REST** con FastAPI. El bot corre en Docker con reinicio automático. En el futuro próximo: multi-usuario, tracking personal, IA y gamificación RPG.

---

## ✨ Funcionalidades actuales (v0.11.0)

### Bot Telegram

| Comando | Descripción |
|---------|-------------|
| `/start` | Menú principal con botones inline + saludo contextual |
| `/nueva` | Nueva cita: fecha → **franja horaria** → hora → cuartos → nombre → tipo → notas |
| `/citas [fecha]` | Ver citas del día, nav ◀️▶️, vista detalle, borrar/editar |
| `/habito` | Registrar hábito: nombre libre + valor + acumulación `+N` |
| `/habitos [fecha]` | Ver hábitos del día, nav ◀️▶️, borrar/editar/sumar |
| `/semana` | Vista semanal con navegación entre semanas |
| `/resumen [fecha]` | Resumen completo: citas + hábitos |
| `/config` | Configurar tipos de hábitos con botones rápidos |
| `/cancelar` | Cancela cualquier operación en curso |

**Fechas aceptadas:** `hoy`, `mañana`, `ayer`, `27/03`, `2026-04-12`, `lunes`, `el viernes`…

**Hábitos acumulables:** escribe `+2` para sumar al valor existente, o el valor directo para sobreescribir.

**Franjas horarias en /nueva:**
```
Fecha → [🌅 Mañana 6-14] [🌆 Tarde 14-22] [🌙 Noche 22-6] [✏️ Exacta]
          ↓
       Hora en punto → Cuartos (:00 :15 :30 :45) → Nombre → Tipo → Notas
```

### API REST (FastAPI)

```
Citas:
  POST   /appointments/{date}                → crear cita
  GET    /appointments/{date}                → citas del día
  GET    /appointments/week/{date}           → citas de la semana (lun–dom)
  GET    /appointments/range/{from}/{to}     → citas en rango
  GET    /appointments/upcoming/{date}       → próximas citas
  PUT    /appointments/{date}/{index}        → editar cita
  DELETE /appointments/{date}/{index}        → borrar cita

Hábitos:
  POST   /habits/{date}                      → registrar hábito (upsert)
  GET    /habits/{date}                      → hábitos del día
  GET    /habits/week/{date}                 → hábitos de la semana
  GET    /habits/range/{from}/{to}           → hábitos en rango
  GET    /habits/stats/{habit}?days=30       → historial de un hábito
  PUT    /habits/{date}/{habit}              → actualizar valor
  DELETE /habits/{date}/{habit}              → borrar hábito

Resumen:
  GET    /summary/{date}                     → citas + hábitos del día
  GET    /summary/week/{date}                → resumen de la semana
```

---

## 🚀 Arranque rápido

### Modo local

```bash
# 1. Clonar
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora

# 2. Entorno virtual + dependencias
python -m venv .venv
source .venv/bin/activate   # Linux/Mac/WSL
make dev

# 3. Variables de entorno
cp .env.example .env
# Editar .env: añadir TELEGRAM_BOT_TOKEN

# 4. Arrancar
make run-api   # terminal 1 → API en http://localhost:8000
make run-bot   # terminal 2 → Bot Telegram
```

### Modo Docker

```bash
cp docker/.env.docker.example .env
# Editar .env: añadir TELEGRAM_BOT_TOKEN

make docker-build   # construir imagen
make docker-up      # arrancar api + bot en segundo plano
make docker-logs    # ver logs en vivo
make docker-down    # parar todo
```

---

## 🗂️ Estructura del proyecto

```
thdora/
├── src/
│   ├── api/              ← FastAPI: routers, modelos, deps
│   │   └── routers/      ← appointments.py, habits.py, summary.py
│   ├── bot/              ← Bot Telegram
│   │   ├── main.py       ← entrypoint
│   │   ├── api_client.py ← cliente HTTP asíncrono
│   │   ├── keyboards.py  ← todos los teclados inline
│   │   ├── utils/        ← dates.py, accum.py
│   │   └── handlers/     ← menu, citas, habitos, semana, config, common
│   ├── core/             ← abstracción + implementaciones
│   │   └── impl/         ← SQLiteLifeManager (activo)
│   └── db/               ← SQLAlchemy: base.py, models.py
├── tests/
│   ├── unit/bot/         ← test_dates, test_accum, test_keyboards
│   └── bot/              ← test_handlers_citas, _habitos, _menu
├── docker/               ← entrypoints + .env.docker.example
├── data/                 ← thdora.db (SQLite, no versionado)
├── docs/                 ← diarios, architecture, INDEX.md
├── Dockerfile
├── docker-compose.yml
├── COMO_PROCEDER.md      ← ⭐ empieza aquí
├── ROADMAP.md
├── CHANGELOG.md
├── pyproject.toml
└── Makefile
```

---

## 🧪 Tests

```bash
make test          # todos los tests
make test-bot      # solo tests del bot (sin API ni Telegram real)
make test-cov      # con cobertura → htmlcov/index.html
```

---

## 🗣️ Hoja de ruta

| Fase | Estado | Descripción |
|------|--------|-------------|
| F1–F9.7 | ✅ | Base, API REST, SQLite, Bot completo, Docker |
| F9.8 | 🔒 | **Multi-usuario** — bloqueado hasta prueba en vivo |
| F10 | ⏳ | Módulo Tracking personal (sueño, estado, estudio) |
| F11 | ⏳ | Notificaciones proactivas (APScheduler) |
| F12 | ⏳ | IA conversacional (Groq / Whisper) |
| F13 | ⏳ | Gamificación RPG (XP, niveles, rachas) |
| F14–F16 | ⏳ | Telegram Mini App → PWA → React Native |

---

## 📚 Documentación

- [📍 Cómo proceder](COMO_PROCEDER.md) — arranque + checklist + siguiente paso
- [🗺️ ROADMAP](ROADMAP.md) — visión completa F1→F16
- [📝 CHANGELOG](CHANGELOG.md) — historial de versiones
- [🗂️ Índice docs](docs/INDEX.md) — diarios, arquitectura, módulos

---

## 📄 Licencia

MIT — Álvaro Fernández Mota, 2026
