# 🧭 THDORA — CÓMO PROCEDER

> Guía de trabajo para retomar el proyecto en cualquier momento sin perder contexto.
> Última actualización: **14 junio 2026 — 22:16 CEST**

---

## Estado actual — v0.16.3 ✅ ACTIVO EN MADRE

```
✅ Bot Telegram       → src/bot/main.py (polling, PTB v20+)
✅ FastAPI            → src/api/ (5 routers completos)
✅ SQLite             → data/thdora.db (volumen Docker persistente)
✅ Groq client        → src/ai/groq_client.py
✅ NLP modo Toki      → src/bot/groq_router.py
✅ Scheduler F12      → APScheduler (resumen + evening + citas)
✅ GROQ_API_KEY       → Renovada 14 jun 2026
✅ Docker             → docker compose en Madre (Omarchy)
```

---

## ⭐ Arrancar el proyecto (orden correcto)

```bash
# Ir al proyecto
cd ~/dev/thdora

# Arrancar todos los servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Verificar estado
docker compose ps
# → thdora-api y thdora-bot deben estar Running

# Verificar en Telegram
# → /start → debe responder
# → Texto libre → NLP Toki debe responder (Groq)
```

---

## 🔧 Gestión de servicios

```bash
# Parar todo
docker compose down

# Reiniciar solo el bot
docker compose restart bot

# Rebuild tras cambios de código
docker compose build bot && docker compose up -d bot

# Consola base de datos
docker compose exec api sqlite3 /app/data/thdora.db

# Ver logs de un servicio
docker compose logs -f bot
docker compose logs -f api
```

| Fichero modificado | Rebuild necesario |
|--------------------|-------------------|
| `src/bot/**` | Solo `bot` |
| `src/api/**` | Solo `api` |
| `src/core/**` o `src/db/**` | Ambos |
| `requirements.txt` | Ambos (rebuild completo) |

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

# 4. Rebuild solo el servicio afectado
docker compose build bot
docker compose up -d bot
```

---

## 📋 Próximas tareas (en orden)

### PRIORIDAD 1 — Verificación post-deploy ← AHORA
- [x] ~~Renovar GROQ_API_KEY~~ ✅ 14 jun 2026
- [x] ~~Migrar de Acer a Madre~~ ✅ 14 jun 2026
- [ ] Ejecutar checklist de pruebas en producción (Telegram real)
- [ ] Probar /start y texto libre con NLP Toki
- [ ] Verificar Scheduler F12 activo

### PRIORIDAD 2 — Citas
- [ ] Bloque 1.2 — mostrar horario disponible antes de mover una cita
- [ ] BUG 1 — borrar cita por fecha futura
- [ ] BUG 2 — editar cita con intent genérico

### PRIORIDAD 3 — Reestructuración repo
- [ ] Mover `docs/diarios/` → `.github/diarios/`
- [ ] Mover `docs/sessions/` → `.github/sessions/`
- [ ] Mover `docs/auditoria/` → `.github/auditoria/`
- [ ] Mover `CLASES_BEGO.md` + `GUIA_BEGO.md` → `.github/archive/`
- [ ] Borrar `docs/ROADMAP.md` (duplicado de raíz)

### PRIORIDAD 4 — BD real
- [ ] Alembic — migraciones en `src/db/migrations/`
- [ ] PostgreSQL en producción
- [ ] Tests de integración con BD real

### PRIORIDAD 5 — Features
- [ ] Handler `/desahogo` → rimas/letras (Groq)
- [ ] Soporte Ollama como alternativa local
- [ ] Multiusuario — API con `user_id` de Telegram

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
    └── desahogo      → [PENDIENTE]
    └── desconocido   → mostrar menú del bot
```

### Cómo añadir un nuevo intent
1. Añadir nombre al `_CLASSIFY_SYSTEM` en `groq_router.py`
2. Añadir rama en `route()` con su función de extracción
3. Añadir handler en `nlp.py`

---

## Variables de entorno (`.env`)

```bash
TELEGRAM_BOT_TOKEN=xxx
GROQ_API_KEY=gsk_xxx       # renovar en console.groq.com cuando caduque
# THDORA_API_URL no va aquí — definida en docker-compose.yml como http://api:8000
```

---

## 📌 Contexto del proyecto

- **Stack:** Python 3.11 | python-telegram-bot v20 | FastAPI | SQLAlchemy | SQLite→PostgreSQL | Groq
- **Servidor:** Madre — Omarchy (Arch + Hyprland), i5-8400, 16GB, GTX 1060 · IP Tailscale `100.91.112.32`
- **Ruta local:** `~/dev/thdora`
- **Repo:** [github.com/alvarofernandezmota-tech/thdora](https://github.com/alvarofernandezmota-tech/thdora)
- **Visión:** Asistente personal IA multi-plataforma. Base privada que alimenta expresión pública.

---

_Actualizado: 14 junio 2026 — 22:16 CEST_
