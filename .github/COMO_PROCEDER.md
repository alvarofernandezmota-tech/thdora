# 🧭 THDORA — CÓMO PROCEDER

> Guía de trabajo para retomar el proyecto en cualquier momento sin perder contexto.
> Última actualización: **27 abril 2026 — 20:15 CEST**

---

## Estado actual — v0.16.0 ✅ 24/7 Docker

```
✅ API FastAPI        → http://localhost:8001 (en servidor Acer)
✅ Bot Telegram       → polling 24/7
✅ SQLite             → data/thdora.db
✅ Scheduler F12      → APScheduler (resumen + evening + citas)
✅ groq_router.py    → NLP modo Toki con contexto real
⚠️ GROQ_API_KEY       → caducada — NLP degradado a menú
```

### Arrancar el proyecto

```bash
# Terminal 1 — API
make run-api

# Terminal 2 — Bot
make run-bot

# Con Docker (producción)
docker compose up -d
docker compose logs -f
```

---

## 🌿 Estrategia de ramas — Desarrollo sin romper producción

> **Regla de oro:** nunca tocar código en `main` directamente.
> `main` = lo que está corriendo. `dev` = donde se trabaja.

### Flujo completo de trabajo

```bash
# 1. Siempre arrancar desde dev
git checkout dev
git pull origin main          # sincronizar con lo último de prod

# 2. Hacer cambios, commits normales
git add .
git commit -m "fix: descripción del cambio"
git push origin dev

# 3. Cuando está probado y listo → merge a main
git checkout main
git merge dev
git push origin main

# 4. En el servidor: rebuild SOLO el servicio afectado
docker compose build bot      # si solo tocaste src/bot/
docker compose up -d bot      # reinicia SOLO el bot — API sigue viva ✅
```

### Qué rebuild según el fichero tocado

| Fichero modificado | Rebuild necesario |
|--------------------|-------------------|
| `src/bot/**` | Solo `bot` |
| `src/api/**` | Solo `api` |
| `src/core/**` o `src/db/**` | Ambos (`api` + `bot`) |
| `requirements.txt` | Ambos (rebuild completo) |

---

## 🔴 Bugs conocidos (pendientes)

| # | Severidad | Descripción | Ficheros |
|---|-----------|-------------|----------|
| BUG 1 | 🔴 CRÍTICO | Borrar cita por fecha futura no funciona | `citas.py` + `groq_router.py` |
| BUG 2 | 🔴 CRÍTICO | Editar cita con intent genérico falla | `citas.py` + `groq_router.py` |
| BUG 3 | 🟡 MEDIO | Cita duplicada en vista mensual | `src/api/` |
| BUG 4 | 🟢 BAJO | Hábito sin tipo muestra texto raro | `habitos.py` |
| WARN | ℹ️ INFO | PTBUserWarning per_message=False (5 handlers) | `citas.py`, `habitos.py`, `config.py` |

---

## 🤖 Arquitectura NLP actual (modo Toki)

```
Usuario escribe texto
    ↓
nlp_handler() — handlers/nlp.py
    ↓
⏳ Procesando... (feedback inmediato)
    ↓
_get_api_context()  ←── 3 llamadas paralelas a la API
    ├── get_appointments(hoy)
    ├── get_appointments(mañana)
    └── get_habits(hoy)
    ↓
groq_router.route(text, user_data, api_context)
    ↓
① llama-3.1-8b-instant → clasificar intent
    ├── nueva_cita      → extract_cita()   → api.create_appointment()
    ├── log_habito      → extract_habito() → api.log_habit()
    ├── borrar_cita     → [BUG 1]
    ├── editar_cita     → [BUG 2]
    ├── consulta/chat   → chat_response(contexto real)
    └── desconocido     → mostrar menú del bot
```

### Cómo añadir un nuevo intent
1. Añadir nombre al `_CLASSIFY_SYSTEM` en `groq_router.py`
2. Añadir rama en `route()` con su función de extracción
3. Añadir handler en `nlp.py`

---

## Variables de entorno

```bash
# Obligatorias
TELEGRAM_BOT_TOKEN=xxx
GROQ_API_KEY=gsk_xxx       # ⚠️ CADUCADA — renovar en groq.com
THDORA_API_URL=http://api:8000
THDORA_DB_PATH=data/thdora.db
```

---

_Actualizado: 27 abril 2026 — 20:15 CEST — movido a .github/ (Bloque 3.2)_
