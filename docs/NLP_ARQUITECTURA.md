# 🤖 THDORA — Arquitectura NLP / IA

> **Última actualización: 14 abril 2026 — v0.15.1**
> Fichero de referencia para retomar el trabajo sin perder contexto.

---

## Resumen ejecutivo

THDORA usa una arquitectura **multi-modelo orquestada** donde cada modelo hace lo que mejor sabe hacer.
La base es **100% gratuita** usando Groq. Los proveedores de pago son opcionales y activables por variable de entorno.

---

## Arquitectura de modelos — Fase 1 (actual, todo Groq gratis)

```
Mensaje del usuario
       ↓
① llama-3.1-8b-instant       → clasifica intent en <50ms
   nueva_cita / log_habito / consulta / chat / desconocido
       ↓
② llama-3.3-70b-versatile    → extrae JSON o responde en chat
   {"date": "2026-04-15", "time": "17:00", "name": "Dentista", ...}
       ↓
③ api_client.py               → llamada a FastAPI (sin IA)
       ↓
✓ Respuesta al usuario
```

### Memoria conversacional
- Los últimos **10 mensajes** (5 turnos) se guardan en `context.user_data["nlp_history"]`.
- Se envían a Groq en cada llamada → el modelo entiende referencias como “cámbiala”.
- `PicklePersistence` activo desde v0.13 → el historial **sobrevive reinicios del bot**.

---

## Ficheros implementados

| Fichero | Función |
|---|---|
| `src/bot/groq_router.py` | Orquestador: `classify_intent` + `extract_cita` + `extract_habito` + `chat_response` + `route()` |
| `src/bot/handlers/nlp.py` | Handler Telegram: recibe resultado del router y actúa |
| `src/bot/main.py` | `_route_free_text()` — prioridad: acum_hab → NLP |

---

## Intents y acciones

| Intent | Modelo | Acción |
|---|---|---|
| `nueva_cita` | 8b → 70b | Extrae JSON → `api.create_appointment()` + check solapamiento |
| `log_habito` | 8b → 70b | Extrae JSON → `api.log_habit()` |
| `consulta` | 8b → 70b | Respuesta conversacional con **contexto real** de la API |
| `chat` | 8b → 70b | Respuesta conversacional con **contexto real** de la API |
| `desconocido` | 8b | Muestra menú del bot (no genera texto libre) |

---

## Contexto real en consultas (v0.14)

Antes de responder a intents `consulta` y `chat`, el bot obtiene los datos reales del día:

```python
# nlp.py — _get_api_context(today, tomorrow)
async with asyncio.gather(
    get_appointments(today),
    get_appointments(tomorrow),
    get_habits(today)
) as results:
    ...
```

Ese contexto se inyecta en el system prompt de Groq antes de la llamada.
Si la API falla, el bot usa el prompt base sin contexto (degradación elegante).

Intent `desconocido` → desde v0.14 muestra directamente `📍 Menú principal` con teclado.
Nunca genera texto genérico del tipo “No entendí tu mensaje”.

---

## Detección de conflicto de cita (v0.15.0 → v0.15.1)

### Solapamiento real (v0.15.0 — `appointments.py`)

La API calcula solapamiento con duración, no solo hora exacta:

```
new_start < exist_end  AND  new_end > exist_start
```

- Duración predeterminada: 60 minutos (`_DEFAULT_DURATION_MIN`).
- El endpoint acepta `?duration=N` para citas de duración variable.
- Cubre todos los casos: hora exacta, inicio dentro del bloque, nueva tapa inicio de otra.

### Mensaje enriquecido + horario visual (v0.15.1 — `citas.py` / `nlp.py`)

Cuando hay conflicto, el bot muestra:

```
⚠️ Las 17:30 solapan con Dentista (17:00–18:00)

🗓 Agenda del 15/04/2026
│ 08:00  🟢 Libre
│ 09:00  🔴 Reunión (09:00–10:00)
│ ...
│ 17:00  🔴 Dentista
│ 17:30  ⚠️  ┃
│ 18:00  🟢 Libre
```

Funciones clave en `nlp.py`:
- `_build_day_schedule(citas, date_str, highlight_time, duration)` — franjas de 30 min, 08:00–22:00.
- `_end_time(start, duration)` — calcula hora de fin para mostrar en el mensaje.
- `_time_to_min(t)` — helper de conversión.

Helper centralizado en `citas.py`:
- `_check_and_show_conflict(obj, context, date_str, time_str, is_message)` — usado tanto
  en `/nueva` como en **editar hora** (fix v0.15.1).

---

## UX del flujo NLP (acumulado v0.12–v0.15.1)

| Situación | Comportamiento |
|---|---|
| Hora no detectada ("00:00") | Pide confirmación al usuario, no crea cita a medianoche |
| Mientras Groq procesa | Muestra `⏳ Procesando...` y lo borra al recibir respuesta |
| Conflicto de cita | Mensaje con rango real + horario visual del día |
| Intent desconocido | Muestra menú del bot directamente |
| Consulta sobre agenda | Obtiene datos reales antes de responder |
| Reinicio del bot | Historial NLP persiste (PicklePersistence) |

---

## Ejemplos de uso

```
Usuario: "mañana dentista a las 5"
Intent:  nueva_cita
JSON:    {"date": "2026-04-15", "time": "17:00", "name": "Dentista", "type": "medica", "notes": ""}
Bot:     ✅ Dentista el 15/04 a las 17:00 — 🏥 Médica

Usuario: "dormí 7 horas"
Intent:  log_habito
JSON:    {"date": "2026-04-14", "habit": "Sueño", "value": "7h"}
Bot:     ✅ Sueño: 7h — 14/04/2026

Usuario: "¿qué tengo mañana?"
Intent:  consulta
Bot:     💬 [Llama 3.3 70B con citas reales del día siguiente]

Usuario: "cámbiala a las 6"  ← entiende contexto del historial
Intent:  nueva_cita (o chat)
Bot:     [actúa en consecuencia]
```

---

## Arquitectura futura — Fase 2 (multi-proveedor opcional)

```
GROQ_API_KEY       → Fase 1 base (clasificar + extraer, gratis)
OPENROUTER_API_KEY → DeepSeek R1 (chat mejorado, gratis) + Perplexity Sonar (internet, gratis)
ANTHROPIC_API_KEY  → Claude Sonnet 4.5 (conversación premium, de pago, opcional)
GEMINI_API_KEY     → Gemini 2.0 Flash (chat alternativo, gratis 1M tokens/mes)
```

### Por qué OpenRouter en lugar de APIs directas
- Una sola API key para 100+ modelos.
- Formato OpenAI-compatible → sin cambios en el código.
- Incluye DeepSeek R1 (gratis, calidad top), Perplexity Sonar (gratis, con internet).
- Fácil A/B testing de modelos.

### Por qué NO se usa ChatGPT/OpenAI directamente
- De pago desde el primer token.
- Groq es ~10x más rápido y gratis.
- Para conversación premium → Claude Sonnet 4.5 tiene mejor tono en español.

---

## Voz (F15 — futuro)

Groq ofrece `whisper-large-v3-turbo` a $0.04/hora.
El flujo es trivial una vez el NLP texto está probado:

```python
audio_file = await update.message.voice.get_file()
transcription = await groq_client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-large-v3-turbo",
    language="es"
)
await route(transcription.text, context.user_data)
```

Sin cambios en la lógica de intents. El router no sabe si el input viene de texto o voz.

---

## Para activar ahora mismo

```bash
# 1. Conseguir API key gratuita en https://console.groq.com
# 2. Añadir al .env
echo "GROQ_API_KEY=gsk_xxxxxxxxxxxx" >> .env

# 3. Instalar dependencia
pip install groq

# 4. Reiniciar el bot
git pull
python -m src.bot.main

# 5. Probar en Telegram
# Escribir: "mañana dentista a las 5"
```

---

_Última actualización: 14 abril 2026 — 18:32 CEST (v0.15.1)_
