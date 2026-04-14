# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.12.0 (14 abril 2026)

```
Bot Telegram (9 comandos + 5 ConversationHandlers + inline buttons + NLP texto libre)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
    ↕ Groq API (NLP gratuito)
GroqRouter (intent + entidades + chat conversacional)
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
- **Código modular** — `src/bot/handlers/` package (7 módulos) + `keyboards.py` + `utils/`
- **➕ Nueva cita desde botón del menú** — arranca ConversationHandler directamente ✅
- **➕ Nuevo hábito desde botón del menú** — arranca ConversationHandler directamente ✅
- **Menú operativo al 100%** — probado en vivo ✅
- **🤖 NLP con Groq** — texto libre → citas/hábitos/chat ✅ (código listo, requiere GROQ_API_KEY)

---

## ✅ Completadas

### F1–F9.8 — Base, API, Bot, Persistencia, Documentación
> Ver historial completo en [CHANGELOG.md](CHANGELOG.md)

### F12 — Notificaciones proactivas ✅ (14 abril 2026)
- [x] `UserConfig` en SQLite (horarios resumen + evening)
- [x] APScheduler integrado en bot
- [x] Jobs diarios: resumen mañana + evening log
- [x] Jobs one-shot por cita (aviso 15 min antes)
- [x] `/config` → rama notificaciones con horarios configurables
- [x] Scheduler arranca en `post_init` (sin RuntimeError)

### F13-base — NLP con Groq ✅ (14 abril 2026)

> Arquitectura decidida y código base implementado.
> Requiere `GROQ_API_KEY` en `.env` para activarse.

**Ficheros creados:**
- [x] `src/bot/groq_router.py` — orquestador NLP (intent + entidades + chat)
- [x] `src/bot/handlers/nlp.py` — handler de Telegram para texto libre
- [x] `src/bot/main.py` — `_route_free_text` conectado a NLP

**Arquitectura de modelos (todo Groq, 100% gratis):**
```
① llama-3.1-8b-instant     → clasificar intent  (~560 t/s)
② llama-3.3-70b-versatile  → extraer entidades + chat conversacional
③ context.user_data        → memoria últimos 10 mensajes
```

**Intents soportados:**
- `nueva_cita`  → extrae fecha/hora/nombre/tipo → `api.create_appointment()`
- `log_habito`  → extrae fecha/hábito/valor → `api.log_habit()`
- `consulta`    → respuesta conversacional con contexto
- `chat`        → chat libre con Llama 3.3 70B
- `desconocido` → pide aclaración al usuario

**Para activar en local:**
```bash
echo "GROQ_API_KEY=tu_key_aqui" >> .env
pip install groq
git pull && python -m src.bot.main
```

---

## 🔶 En curso / Próximo

### F13-test — Probar NLP en Telegram real 🔜 SIGUIENTE

> El código está en main. Solo falta la API key y probarlo.

- [ ] Añadir `GROQ_API_KEY` al `.env` local
- [ ] `pip install groq` en el entorno
- [ ] Probar: `"mañana dentista a las 5"` → cita creada ✅
- [ ] Probar: `"dormí 7 horas"` → hábito registrado ✅
- [ ] Probar: `"¿qué tengo mañana?"` → respuesta conversacional ✅
- [ ] Probar: `"cámbiala a las 6"` → entiende contexto con historial ✅
- [ ] Actualizar `.env.example` con `GROQ_API_KEY`
- [ ] Añadir `groq` a `requirements.txt`

---

### F13-v2 — Expansión NLP 🔜

> Una vez probado el NLP base, añadir estas mejoras:

**Modelos adicionales (opcionales, activables por variable de entorno):**

| Variable | Proveedor | Modelo | Cuándo activar |
|---|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter | `deepseek/deepseek-r1` | Chat conversacional mejorado (gratis) |
| `OPENROUTER_API_KEY` | OpenRouter | `perplexity/sonar` | Consultas con acceso a internet (gratis) |
| `ANTHROPIC_API_KEY` | Anthropic | `claude-sonnet-4-5` | Conversación premium (de pago, opcional) |
| `GEMINI_API_KEY` | Google | `gemini-2.0-flash` | Chat alternativo (gratis 1M tokens/mes) |

**Mejoras de NLP:**
- [ ] Detectar intent `editar_cita` ("cambia la cita del dentista")
- [ ] Detectar intent `borrar_cita` ("borra la cita de mañana")
- [ ] Detectar intent `consulta_habitos` ("¿cuánto dormí esta semana?")
- [ ] Responder consultas con datos reales de la API (inject contexto)
- [ ] Persistir historial conversacional en SQLite (no solo en memoria)

**Acceso a internet:**
- [ ] Integrar OpenRouter `perplexity/sonar` para preguntas factuales
- [ ] Opción self-hosted: Perplexica + SearxNG (gratis, sin API key)

---

### F15 — Voz (Whisper) 🔜

> Groq ya ofrece `whisper-large-v3-turbo` a $0.04/hora.
> Una vez el NLP texto esté probado, añadir soporte de audio.

- [ ] Handler de mensajes de voz en Telegram (`filters.VOICE`)
- [ ] Descargar audio del mensaje → transcribir con Groq Whisper
- [ ] Pasar transcripción a `groq_router.route()` como texto normal
- [ ] Sin cambios en la lógica de intents

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

### F14 — Módulo Tracking personal 🔜

> sueño, sustancias, estado, estudio, proyecto

- [ ] `src/db/models.py` — tabla `daily_tracking`
- [ ] `src/api/routers/tracking.py` — endpoints CRUD
- [ ] `src/bot/handlers/tracking.py` — formulario guiado
- [ ] Sistema de puntuación diaria (0–10)
- [ ] Dashboard tracking — tendencias + racha

---

### F16 — Gamificación RPG 🔜
- XP por hábitos cumplidos (campo `xp_rule` ya modelado en `HabitConfig`)
- Niveles: 🐣 Novato → 👑 Leyenda
- Rachas diarias + misiones
- Conecta con notif de racha de F12.v1.2

### F17 — Telegram Mini App 🔜
- HTML5/React + `Telegram.WebApp` SDK
- Conectar con API FastAPI existente

### F18 — PWA 🔜
- App instalable en móvil, offline-first

### F19 — React Native 🔜

---

## Orden recomendado de implementación

```
F13-test (probar NLP) → F13-v2 (expandir NLP) → F15 (Voz Whisper)
    → F10 (Docker 24/7) → F11 (Multi-usuario)
    → F14 (Tracking) → F16 (Gamificación)
    → F17/F18/F19 (Apps)
```

> F13-test primero: el código ya está, solo falta la API key.
> F15 (voz) después de NLP porque usa el mismo router.
> F10 antes de F11 para no tener que migrar dos veces.

---

_Última actualización: 14 abril 2026 — 11:46 CEST_
