# 🧭 THDORA — CÓMO PROCEDER

> Guía de trabajo para retomar el proyecto en cualquier momento sin perder contexto.
> Última actualización: **31 mayo 2026 — 20:55 CEST**

---

## Estado actual — v4.3 ⚠️ GROQ KEY CADUCADA

```
✅ Bot Telegram       → src/bot/main.py (polling, PTB v20+)
✅ FastAPI            → src/api/ (5 routers completos)
✅ SQLite             → data/thdora.db
✅ Groq client        → src/ai/groq_client.py
✅ NLP modo Toki      → src/bot/groq_router.py (34KB)
✅ Scheduler F12      → APScheduler (resumen + evening + citas)
✅ .venv instalado    → ~/projects/thdora/.venv
⚠️ GROQ_API_KEY        → CADUCADA — renovar en console.groq.com
```

### ⭐ Arrancar el proyecto (orden correcto)

```bash
# 0. Ir al proyecto y activar entorno
cd ~/projects/thdora
source .venv/bin/activate

# 1. Actualizar GROQ_API_KEY en .env
nano .env
# → GROQ_API_KEY=gsk_nueva_key_aqui

# Terminal 1 — API
make run-api

# Terminal 2 — Bot
make run-bot

# Verificar que funciona
# → Abrir Telegram → /start → debe responder
# → Escribir texto libre → debe responder con NLP (Groq)

# Dejar corriendo en segundo plano
screen -S thdora-api
make run-api
# Ctrl+A D para salir sin matar

screen -S thdora-bot
make run-bot
# Ctrl+A D para salir sin matar
```

---

## 📋 Próximas tareas (en orden)

### PRIORIDAD 1 — Activación (mañana 1 junio)
- [ ] Renovar GROQ_API_KEY en console.groq.com
- [ ] `make run-api` + `make run-bot`
- [ ] Probar /start y texto libre en Telegram
- [ ] Dejar con `screen` en segundo plano

### PRIORIDAD 2 — Features nuevas
- [ ] Handler `/desahogo` → rimas/letras con lo que sientes (Groq)
- [ ] Soporte Ollama como alternativa local a Groq
- [ ] Resolver BUG 1 y BUG 2 (borrar/editar citas)

### PRIORIDAD 3 — BD real
- [ ] Migraciones en src/db/migrations/
- [ ] PostgreSQL en producción (docker-compose ya configurado)
- [ ] Tests de integración con BD real

### PRIORIDAD 4 — Deploy
- [ ] Railway.app (gratis, sube solo desde GitHub)
- [ ] O mantener en servidor Acer con Docker

---

## 🌿 Estrategia de ramas — Desarrollo sin romper producción

> **Regla de oro:** nunca tocar código en `main` directamente.
> `main` = lo que está corriendo. `dev` = donde se trabaja.

```bash
# 1. Siempre arrancar desde dev
git checkout dev
git pull origin main

# 2. Hacer cambios y commits
git add .
git commit -m "feat: descripción del cambio"
git push origin dev

# 3. Cuando está probado → merge a main
git checkout main
git merge dev
git push origin main

# 4. Rebuild SOLO el servicio afectado
docker compose build bot
docker compose up -d bot
```

| Fichero modificado | Rebuild necesario |
|--------------------|-------------------|
| `src/bot/**` | Solo `bot` |
| `src/api/**` | Solo `api` |
| `src/core/**` o `src/db/**` | Ambos |
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

## 🤖 Arquitectura NLP (modo Toki)

```
Usuario escribe texto
    ↓
nlp_handler() — handlers/nlp.py
    ↓
⏳ Procesando... (feedback inmediato)
    ↓
_get_api_context()  ←── 3 llamadas paralelas
    ├── get_appointments(hoy)
    ├── get_appointments(mañana)
    └── get_habits(hoy)
    ↓
groq_router.route(text, user_data, api_context)
    ↓
① llama-3.1-8b-instant → clasificar intent
    ├── nueva_cita    → extract_cita()   → api.create_appointment()
    ├── log_habito    → extract_habito() → api.log_habit()
    ├── borrar_cita   → [BUG 1]
    ├── editar_cita   → [BUG 2]
    ├── consulta/chat → chat_response(contexto real)
    └── desahogo      → [PENDIENTE — rimas/letras]
    └── desconocido   → mostrar menú del bot
```

### Cómo añadir un nuevo intent
1. Añadir nombre al `_CLASSIFY_SYSTEM` en `groq_router.py`
2. Añadir rama en `route()` con su función de extracción
3. Añadir handler en `nlp.py`

---

## Variables de entorno

```bash
TELEGRAM_BOT_TOKEN=xxx
GROQ_API_KEY=gsk_xxx       # ⚠️ CADUCADA — renovar en console.groq.com
THDORA_API_URL=http://localhost:8000
THDORA_DB_PATH=data/thdora.db
```

---

## 📌 Contexto del proyecto

- **Stack:** Python 3.11 | python-telegram-bot v20 | FastAPI | SQLAlchemy | SQLite→PostgreSQL | Groq
- **Ruta local:** `~/projects/thdora`
- **Repo:** [github.com/alvarofernandezmota-tech/thdora](https://github.com/alvarofernandezmota-tech/thdora)
- **Diario:** repo `personal` → `01_traking_diario/01_diarios/`
- **Visión:** Asistente personal IA multi-plataforma. Base privada que alimenta expresión pública.

---

_Actualizado: 31 mayo 2026 — 20:55 CEST_
