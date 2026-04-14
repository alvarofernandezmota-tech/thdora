# 🧭 THDORA — CÓMO PROCEDER

> Guía de trabajo para retomar el proyecto en cualquier momento sin perder contexto.
> Última actualización: **14 abril 2026 — 16:14 CEST**

---

## Estado actual — v0.14.0

```
✅ API FastAPI        → http://localhost:8000
✅ Bot Telegram       → polling activo
✅ SQLite             → data/thdora.db
✅ Scheduler F12      → APScheduler (resumen + evening + citas)
✅ groq_router.py    → NLP modo Toki con contexto real
✅ handlers/nlp.py   → handler texto libre + menú en desconocido
✅ GROQ_API_KEY       → configurada y funcionando
```

### Probado en vivo hoy ✅
| Caso | Resultado |
|---|---|
| `Gol` | Menú del bot (intent desconocido) ✅ |
| `¿qué tengo hoy?` | Listó citas y hábitos reales ✅ |
| `tengo gym a las 13` | Detectó conflicto con "soci" ✅ |
| `mañana dentista a las 5` | Creó cita ✅ |
| `dormí 8 horas` | Registró hábito ✅ |

---

## Arrancar el proyecto

```bash
# Terminal 1 — API
make run-api

# Terminal 2 — Bot
make run-bot
```

Tras arrancar, manda `/start` al bot para programar los jobs diarios.

---

## 🔜 LO SIGUIENTE — F13-v2: Mejorar NLP

### Paso 1 — Personalidad más rica (30 min, impacto inmediato)
Editar `_CHAT_SYSTEM_BASE` en `src/bot/groq_router.py`:
- Más proactivo: que sugiera acciones relevantes
- Que recuerde el nombre del usuario
- Respuestas más naturales y menos robóticas
- Instrucciones claras para cada tipo de consulta

### Paso 2 — Nuevos intents (1-2h)
En `groq_router.py`:
```python
# Añadir al clasificador:
- borrar_cita    → "cancela el gym", "borra la cita de mañana"
- editar_cita    → "mueve la peluquería a las 18"
- consulta_semana → "¿qué tengo esta semana?"
```
En `handlers/nlp.py`:
- Handler para cada nuevo intent
- `borrar_cita`: buscar por nombre/fecha + confirmar + `api.delete_appointment()`
- `editar_cita`: buscar + pedir nuevo valor + `api.update_appointment()`

### Paso 3 — Contexto semanal
- En consultas de semana, inyectar `get_appointments()` de los 7 días
- Historial de hábitos de los últimos 7 días

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
    ├── nueva_cita   → extract_cita()  → api.create_appointment()
    ├── log_habito   → extract_habito() → api.log_habit()
    ├── consulta     → chat_response(contexto real)
    ├── chat         → chat_response(contexto real)
    └── desconocido  → mostrar menú del bot
```

### Cómo cambiar la personalidad de THDORA
Edita solo `_CHAT_SYSTEM_BASE` en `src/bot/groq_router.py`.
El cambio tiene efecto inmediato al reiniciar el bot.
No hay que tocar ningún otro módulo.

### Cómo añadir un nuevo intent
1. Añadir el nombre al `_CLASSIFY_SYSTEM` en `groq_router.py`
2. Añadir la rama en `route()` con su función de extracción
3. Añadir el handler correspondiente en `nlp.py`

---

## Variables de entorno

```bash
# Obligatorias
TELEGRAM_BOT_TOKEN=xxx   # token de @BotFather
GROQ_API_KEY=gsk_xxx     # console.groq.com — gratis ✅ configurada

# Opcionales (para cuando se quiera expandir)
OPENROUTER_API_KEY=xxx   # openrouter.ai — gratis
ANTHROPIC_API_KEY=xxx    # anthropic.com — de pago
GEMINI_API_KEY=xxx       # aistudio.google.com — gratis

# Configuración
THDORA_API_URL=http://localhost:8000  # por defecto
```

---

## Estructura de ficheros relevantes

```
thdora/
├── src/bot/
│   ├── main.py              ← entrypoint bot
│   ├── api_client.py        ← llamadas HTTP a FastAPI
│   ├── groq_router.py       ← orquestador NLP modo Toki
│   ├── scheduler.py         ← APScheduler F12
│   ├── keyboards.py         ← teclados Telegram
│   └── handlers/
│       ├── nlp.py           ← handler texto libre
│       ├── menu.py
│       ├── citas.py
│       ├── habitos.py
│       ├── semana.py
│       ├── config.py
│       └── common.py
├── src/api/                 ← FastAPI
├── src/db/                  ← SQLAlchemy + SQLite
├── docs/
│   ├── NLP_ARQUITECTURA.md  ← decisiones IA
│   ├── INDEX.md
│   ├── FLUJOS_DETALLADOS.md
│   ├── API_REFERENCE.md
│   └── CONVENCIONES.md
├── ROADMAP.md               ← qué viene
├── CHANGELOG.md             ← qué se hizo
└── COMO_PROCEDER.md         ← estás aquí
```

---

## Warnings conocidos (no críticos)

```
PTBUserWarning: per_message=False en ConversationHandler
```
No afecta al funcionamiento. Se arregla añadiendo `per_message=True`
a los `CallbackQueryHandler` internos de `citas.py`, `habitos.py` y `config.py`.
No es urgente.

---

_Actualizado: 14 abril 2026 — 16:14 CEST — post pruebas v0.14.0 en vivo_
