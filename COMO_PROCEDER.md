# 🧭 THDORA — CÓMO PROCEDER

> Guía de trabajo para retomar el proyecto en cualquier momento sin perder contexto.
> Última actualización: **14 abril 2026 — 23:35 CEST**

---

## Estado actual — v0.14.0

```
⛔ Bot PARADO manualmente a las ~23:30 del 14/04/2026
✅ API FastAPI        → http://localhost:8000 (cuando arranca)
✅ Bot Telegram       → polling (cuando arranca)
✅ SQLite             → data/thdora.db
✅ Scheduler F12      → APScheduler (resumen + evening + citas)
✅ groq_router.py    → NLP modo Toki con contexto real
✅ handlers/nlp.py   → handler texto libre + menú en desconocido
✅ GROQ_API_KEY       → configurada y funcionando
```

### Arrancar el proyecto

```bash
# Terminal 1 — API
make run-api

# Terminal 2 — Bot
make run-bot
```

---

## 🔴 Bugs confirmados en producción — Sesión 14 abril noche

Estos bugs se vieron en el chat real de Telegram esta noche. Prioridad para mañana.

### BUG 1 🔴 CRÍTICO — Borrar cita por fecha futura no funciona
```
Alvaro: "Elimina la del 15 de abril"  → FALLA
Alvaro: "Borra dentista"              → FALLA
Alvaro: "Cancela el gym de hoy"       → funciona ✅
```
El intent `borrar_cita` solo acepta referencias relativas (hoy/mañana).
No extrae fechas futuras concretas ni nombres sin fecha.

**Ficheros:** `src/bot/handlers/citas.py` + `src/bot/groq_router.py`

---

### BUG 2 🔴 CRÍTICO — Editar cita solo acepta formato exacto
```
Alvaro: "Quiero cambiar una cita"     → FALLA
Alvaro: "Modifica la cita dentista"   → FALLA
Alvaro: "Mueve el gym de hoy a las 18" → funciona ✅
```
Cuando el usuario dice intent genérico ("quiero editar una cita") debería
abrir flujo interactivo preguntando cuál y a qué hora. Ahora falla.

**Ficheros:** `src/bot/handlers/citas.py` + `src/bot/groq_router.py`

---

### BUG 3 🟡 MEDIO — Dentista duplicado en vista mensual
```
Alvaro: "Este mes que tengo"
THDORA: 15 de abril (mañana): 17:00 Dentista
         15 de abril (día siguiente): 17:00 Dentista  ← duplicado
```
Posible query SQL con JOIN duplicando filas, o lógica de
"mañana" vs "día siguiente" devolviendo el mismo día dos veces.

**Ficheros:** `src/api/` endpoint de citas por mes

---

### BUG 4 🟢 BAJO — Hábito sin tipo muestra texto raro
```
THDORA: "1 vez de algo (no especificado)"
```
Un hábito se guardó sin tipo. Hay que validar al guardar
y mejorar el formateo si el tipo es null.

**Ficheros:** `src/bot/handlers/habitos.py`

---

### WARN — PTBUserWarning en 5 handlers (no crítico)
```
citas.py:745, 785 — per_message=False en ConversationHandler
habitos.py:478, 506 — per_message=False
config.py:403 — per_message=False
```
No rompe nada. Añadir `per_message=True` cuando se toquen esos handlers.

---

## ✅ Lo que SÍ funciona (confirmado esta noche)

| Caso | Resultado |
|---|---|
| Citas de hoy | ✅ |
| Citas de mañana | ✅ |
| Citas de la semana | ✅ |
| Ver citas por nombre ("citas con el dentista") | ✅ |
| Añadir hábito ("ejercicio 1h") | ✅ 201 Created |
| API todos los endpoints | ✅ 200 OK |
| Scheduler F12 | ✅ |
| NLP intents básicos | ✅ |

---

## 🤖 Plan de mañana — Claude Code arregla los bugs

Mañana usamos **Claude Code** (agente de código autónomo) apuntado a este repo
para resolver los 4 bugs. Claude Code escanea el repo entero solo, decide qué
tocar y hace los commits.

```bash
# 1. Entrar en WSL
wsl
cd ~/projects/thdora

# 2. Instalar Claude Code (si no está)
curl -fsSL https://claude.ai/install.sh | sh
# o: npm install -g @anthropic-ai/claude-code

# 3. Configurar OpenRouter (gratis, sin pagar)
export ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
export ANTHROPIC_API_KEY=sk-or-TU_KEY_AQUI

# 4. Arrancar Claude Code en este repo
claude --model openrouter/mistralai/devstral-2:free
```

**Orden que le pegas a Claude Code:**
```
Escanea este repo completo. Hay 4 bugs confirmados en producción:

1. CRÍTICO: Borrar cita por fecha futura no funciona.
   "Elimina la del 15 de abril" y "Borra dentista" fallan.
   Solo funciona "cancela el dentista de hoy".
   Arregla el intent borrar_cita para aceptar nombre sin fecha y fechas futuras.

2. CRÍTICO: Editar cita no funciona con intent genérico.
   "Quiero editar una cita" debe abrir flujo interactivo.
   Arregla el handler y el intent editar_cita.

3. MEDIO: Dentista duplicado en vista mensual.
   Revisa la query o lógica de fechas.

4. BAJO: Hábito sin tipo muestra "algo (no especificado)".
   Valida al guardar y mejora el formateo.

Por cada fix: cambios mínimos + test + commit separado.
```

---

## Arquitectura NLP actual (modo Toki)

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
    ├── borrar_cita     → [BUG 1] no extrae fecha futura
    ├── editar_cita     → [BUG 2] solo acepta formato exacto
    ├── consulta        → chat_response(contexto real)
    ├── chat            → chat_response(contexto real)
    └── desconocido     → mostrar menú del bot
```

### Cómo cambiar la personalidad de THDORA
Edita solo `_CHAT_SYSTEM_BASE` en `src/bot/groq_router.py`.
Efecto inmediato al reiniciar. No tocar otros módulos.

### Cómo añadir un nuevo intent
1. Añadir nombre al `_CLASSIFY_SYSTEM` en `groq_router.py`
2. Añadir rama en `route()` con su función de extracción
3. Añadir handler en `nlp.py`

---

## Variables de entorno

```bash
# Obligatorias
TELEGRAM_BOT_TOKEN=xxx
GROQ_API_KEY=gsk_xxx       # configurada ✅

# Para Claude Code mañana
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_API_KEY=sk-or-xxx  # openrouter.ai — gratis
```

---

## Estructura de ficheros relevantes

```
thdora/
├── src/bot/
│   ├── main.py              ← entrypoint bot
│   ├── api_client.py        ← llamadas HTTP a FastAPI
│   ├── groq_router.py       ← orquestador NLP modo Toki ⚠️ bugs 1 y 2
│   ├── scheduler.py         ← APScheduler F12
│   ├── keyboards.py         ← teclados Telegram
│   └── handlers/
│       ├── nlp.py           ← handler texto libre
│       ├── citas.py         ← ⚠️ bugs 1 y 2
│       ├── habitos.py       ← ⚠️ bug 4
│       ├── semana.py
│       ├── config.py
│       └── common.py
├── src/api/                 ← FastAPI ⚠️ bug 3 (duplicado mes)
├── src/db/                  ← SQLAlchemy + SQLite
├── docs/
│   ├── NLP_ARQUITECTURA.md
│   ├── FLUJOS_DETALLADOS.md
│   ├── API_REFERENCE.md
│   └── CONVENCIONES.md
├── ROADMAP.md
├── CHANGELOG.md
└── COMO_PROCEDER.md         ← estás aquí
```

---

_Actualizado: 14 abril 2026 — 23:35 CEST — post sesión de noche, bot parado_
