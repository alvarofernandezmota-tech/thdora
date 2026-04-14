# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.14.0 (14 abril 2026)

```
Bot Telegram (9 comandos + 5 ConversationHandlers + inline buttons + NLP texto libre)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
    ↕ Groq API (NLP gratuito)
GroqRouter (intent + entidades + chat conversacional + CONTEXTO REAL modo Toki)
```

### Lo que funciona hoy ✅
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar`
- Saludo contextual (buenos días/tardes/noches)
- Navegación ◀️▶️ con fecha real visible en botón central
- Vista detalle de cita con click en ⏰ hora
- Inline buttons: borrar/editar/sumar citas y hábitos
- Conflicto hora en citas: aviso ⚠️ al crear
- `/semana` con navegación semanal y botones por día
- `/config` para configurar tipos de hábitos con botones rápidos
- Fechas flexibles: `hoy`, `mañana`, `ayer`, `27/03`, nombres de día
- **Datos persistentes en SQLite** — sobreviven a reinicios
- **Scheduler F12** — resumen diario + evening log + avisos citas
- **🤖 NLP Groq — modo Toki (v0.14.0):**
  - Contexto real de API inyectado en el prompt (citas + hábitos hoy y mañana)
  - `¿qué tengo hoy?` → responde con datos reales ✅
  - `mañana dentista a las 5` → crea cita ✅
  - `dormí 7 horas` → registra hábito ✅
  - Detección de conflicto de hora ✅
  - Intent `desconocido` → muestra menú del bot (no texto suelto) ✅
  - 3 llamadas API en paralelo (asyncio.gather) para mínima latencia
  - ⏳ Procesando... feedback inmediato al usuario
  - Fix hora 00:00 → pide confirmación antes de crear

---

## ✅ Completadas

### F1–F12 — Base, API, Bot, Persistencia, Scheduler
> Ver historial completo en [CHANGELOG.md](CHANGELOG.md)

### F13-base — NLP con Groq ✅ (14 abril 2026)
- Clasificador + extractor entidades + chat conversacional
- Intents: `nueva_cita`, `log_habito`, `consulta`, `chat`, `desconocido`

### F13-toki — Modo Toki: contexto real ✅ (14 abril 2026)
- `api_context` inyectado en el prompt de Groq
- `_build_chat_system()` construye el system prompt con datos reales
- Intent `desconocido` → menú del bot, no texto inventado
- Probado en vivo: todos los casos funcionan ✅

---

## 🔶 Siguiente — F13-v2: Mejorar NLP

> El NLP base funciona. Ahora toca expandirlo y pulirlo.

### Prioridad 1 — Personalidad y comprensión (impacto inmediato)
- [ ] Reescribir `_CHAT_SYSTEM_BASE` con personalidad más rica
- [ ] Instrucciones de tono: directo, cercano, proactivo
- [ ] Que sugiera acciones cuando detecte contexto relevante
- [ ] Que recuerde el nombre del usuario en respuestas

### Prioridad 2 — Nuevos intents de acción
- [ ] `borrar_cita` → "cancela el gym de hoy"
- [ ] `editar_cita` → "mueve la peluquería a las 18"
- [ ] `consulta_semana` → "¿qué tengo esta semana?"
- [ ] `borrar_habito` → "quita el registro de agua de hoy"

### Prioridad 3 — Contexto más rico
- [ ] Inyectar también citas de la semana en consultas semanales
- [ ] Historial de hábitos de los últimos 7 días en el contexto
- [ ] Persistir `nlp_history` en SQLite (sobrevive reinicios con más datos)

### Prioridad 4 — Modelos opcionales
| Variable | Proveedor | Modelo | Para qué |
|---|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter | DeepSeek R1 | Chat mejorado (gratis) |
| `GEMINI_API_KEY` | Google | Gemini 2.0 Flash | Alternativa (gratis 1M/mes) |
| `ANTHROPIC_API_KEY` | Anthropic | Claude Sonnet | Premium (de pago) |

---

## 🔜 F15 — Voz (Whisper)

> Groq ya ofrece `whisper-large-v3-turbo` a $0.04/hora.
> Una vez el NLP texto esté pulido, añadir soporte de audio.

- [ ] Handler de mensajes de voz (`filters.VOICE`)
- [ ] Descargar audio → transcribir con Groq Whisper
- [ ] Pasar transcripción a `groq_router.route()` como texto normal
- [ ] Sin cambios en la lógica de intents

---

## 🔜 F10 — Docker + despliegue 24/7

- [ ] `Dockerfile` + `docker-compose.yml`
- [ ] Health checks y reinicio automático
- [ ] Desplegar en VPS (Railway / DigitalOcean / Raspberry Pi)
- [ ] Backup automático de `thdora.db`

---

## 🔜 F11 — Multi-usuario

- [ ] `user_id` en todas las tablas SQLite
- [ ] Middleware en API para `X-User-Id`
- [ ] Onboarding: primer `/start` → configura perfil

> ⚠️ `user_id` ya está pre-modelado en `UserConfig`. Facilita la migración.

---

## 🔜 F14 — Tracking personal

> sueño, sustancias, estado, estudio, proyecto

- [ ] Tabla `daily_tracking` en SQLite
- [ ] Endpoints CRUD en FastAPI
- [ ] Formulario guiado en bot
- [ ] Sistema de puntuación diaria (0–10)

---

## 🔜 F16–F19 — Gamificación, Mini App, PWA, React Native

- F16: XP + niveles + rachas (campo `xp_rule` ya modelado)
- F17: Telegram Mini App (HTML5 + WebApp SDK)
- F18: PWA instalable, offline-first
- F19: React Native

---

## Orden recomendado

```
F13-v2 (mejorar NLP) → F15 (Voz Whisper)
    → F10 (Docker 24/7) → F11 (Multi-usuario)
    → F14 (Tracking) → F16 (Gamificación)
    → F17/F18/F19 (Apps)
```

---

_Última actualización: 14 abril 2026 — 16:14 CEST_
