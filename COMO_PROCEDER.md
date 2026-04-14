# 🧭 THDORA — CÓMO PROCEDER

> Guía de trabajo para retomar el proyecto en cualquier momento sin perder contexto.
> Última actualización: **14 abril 2026**

---

## Estado actual — qué hay funcionando

```
✅ API FastAPI       → http://localhost:8000
✅ Bot Telegram      → polling, v4.0
✅ SQLite            → data/thdora.db
✅ Scheduler F12     → APScheduler (resumen + evening + citas)
✅ groq_router.py   → NLP listo (necesita GROQ_API_KEY)
✅ handlers/nlp.py  → handler texto libre conectado
```

---

## Arrancar el proyecto

```bash
# Terminal 1 — API
uvicorn src.api.main:app --reload

# Terminal 2 — Bot
python -m src.bot.main
```

---

## 🔜 LO MÁS URGENTE — Activar NLP

> El código NLP ya está en GitHub. Solo falta la API key.

```bash
# 1. Ir a https://console.groq.com → crear cuenta gratis → copiar API key

# 2. Añadir al .env
echo "GROQ_API_KEY=gsk_xxxxxxxxxxxx" >> .env

# 3. Instalar dependencia
pip install groq

# 4. Añadir groq al requirements.txt
echo "groq>=0.9.0" >> requirements.txt
git add requirements.txt && git commit -m "deps: añadir groq"

# 5. Reiniciar el bot y probar
python -m src.bot.main
```

**Pruebas a hacer en Telegram:**
- `"mañana dentista a las 5"` → debe crear cita el 15/04 a las 17:00
- `"dormí 7 horas"` → debe registrar Sueño: 7h hoy
- `"¿qué tengo mañana?"` → respuesta conversacional
- `"cámbiala a las 6"` → debe entender contexto anterior

---

## Arquitectura NLP (decisiones tomadas el 14/04/2026)

Ver documentación completa en [`docs/NLP_ARQUITECTURA.md`](docs/NLP_ARQUITECTURA.md)

### Resumen de decisiones

1. **Todo en Groq gratis al principio** — sin coste, sin límites prácticos para uso personal
2. **Dos modelos Groq:**
   - `llama-3.1-8b-instant` → clasificar intent (rápido, barato)
   - `llama-3.3-70b-versatile` → extraer entidades + chat (preciso)
3. **Memoria conversacional** en `context.user_data` — últimos 10 mensajes
4. **Arquitectura abierta** — se pueden añadir Claude, OpenRouter, Gemini después sin tocar el código base

### Proveedores opcionales para más adelante

| Proveedor | Modelo | Para qué | Coste |
|---|---|---|---|
| OpenRouter | DeepSeek R1 | Chat mejorado | Gratis |
| OpenRouter | Perplexity Sonar | Acceso internet | Gratis |
| Google AI Studio | Gemini 2.0 Flash | Chat alternativo | Gratis (1M/mes) |
| Anthropic | Claude Sonnet 4.5 | Conversación premium | ~$0.001/msg |

> Para añadir cualquiera: solo añadir su API key al `.env` y actualizar `groq_router.py`

---

## Próximos pasos ordenados

### Paso 1 — Probar NLP (ahora, 30 minutos)
```
[ ] Conseguir GROQ_API_KEY en console.groq.com
[ ] Añadir al .env + pip install groq
[ ] Probar los 4 casos de uso en Telegram
[ ] Añadir groq a requirements.txt y commitear
```

### Paso 2 — Mejorar NLP (cuando Paso 1 funcione)
```
[ ] Intent editar_cita y borrar_cita
[ ] Consultas con datos reales (inject resumen del día en el prompt)
[ ] Persistir historial en SQLite (no perder contexto al reiniciar)
[ ] Soporte voz con Whisper (ver docs/NLP_ARQUITECTURA.md)
```

### Paso 3 — Docker 24/7 (F10)
```
[ ] Dockerfile + docker-compose.yml
[ ] Desplegar en VPS o Raspberry Pi
[ ] El bot siempre activo sin tener el portátil encendido
```

### Paso 4 — Multi-usuario (F11)
```
[ ] user_id en todas las tablas
[ ] Varias personas usando el mismo bot
```

---

## Variables de entorno

```bash
# Obligatorias
TELEGRAM_BOT_TOKEN=xxx   # token de @BotFather
GROQ_API_KEY=gsk_xxx     # console.groq.com — gratis

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
│   ├── groq_router.py       ← 🆕 orquestador NLP
│   ├── scheduler.py         ← APScheduler F12
│   ├── keyboards.py         ← teclados Telegram
│   └── handlers/
│       ├── __init__.py
│       ├── nlp.py           ← 🆕 handler texto libre
│       ├── menu.py
│       ├── citas.py
│       ├── habitos.py
│       ├── semana.py
│       ├── config.py
│       └── common.py
├── src/api/                 ← FastAPI
├── src/db/                  ← SQLAlchemy + SQLite
├── docs/
│   ├── NLP_ARQUITECTURA.md  ← 🆕 decisiones IA
│   ├── INDEX.md
│   ├── FLUJOS_DETALLADOS.md
│   ├── API_REFERENCE.md
│   └── CONVENCIONES.md
├── ROADMAP.md
├── CHANGELOG.md
└── COMO_PROCEDER.md         ← estás aquí
```

---

_Actualizado: 14 abril 2026 — después de implementar groq_router.py y handlers/nlp.py_
