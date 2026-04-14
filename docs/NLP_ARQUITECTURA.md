# 🤖 THDORA — Arquitectura NLP / IA

> **Decisiones tomadas el 14 abril 2026**
> Fichero de referencia para retomar el trabajo sin perder contexto.

---

## Resumen ejecutivo

THDORA usa una arquitectura **multi-modelo orquestada** donde cada modelo hace lo que mejor sabe hacer. La base es **100% gratuita** usando Groq. Los proveedores de pago son opcionales y activables por variable de entorno.

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
✅ Respuesta al usuario
```

### Memoria conversacional
- Los últimos **10 mensajes** (5 turnos) se guardan en `context.user_data["nlp_history"]`
- Se envían a Groq en cada llamada → el modelo entiende referencias como "cámbiala"
- Sin BBDD extra — todo en memoria PTB (se pierde al reiniciar, suficiente para v1)

---

## Ficheros implementados

| Fichero | Función |
|---|---|
| `src/bot/groq_router.py` | Orquestador: classify_intent + extract_cita + extract_habito + chat_response + route() |
| `src/bot/handlers/nlp.py` | Handler Telegram: recibe resultado del router y actúa |
| `src/bot/main.py` | `_route_free_text()` — prioridad: acum_hab → NLP |

---

## Intents y acciones

| Intent | Modelo usado | Acción |
|---|---|---|
| `nueva_cita` | 8b → 70b | Extrae JSON → `api.create_appointment()` |
| `log_habito` | 8b → 70b | Extrae JSON → `api.log_habit()` |
| `consulta` | 8b → 70b | Respuesta conversacional libre |
| `chat` | 8b → 70b | Respuesta conversacional libre |
| `desconocido` | 8b → 70b | Pide aclaración |

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
Bot:     💬 [respuesta conversacional de Llama 3.3 70B]

Usuario: "cámbiala a las 6"  ← entiende contexto del historial
Intent:  nueva_cita (o chat)
Bot:     [actúa en consecuencia]
```

---

## Arquitectura futura — Fase 2 (multi-proveedor opcional)

Una vez probado el NLP base, se puede activar cualquier proveedor adicional
con solo añadir su API key al `.env`. Sin cambios de código.

```
GROQ_API_KEY       → Fase 1 base (clasificar + extraer, gratis)
OPENROUTER_API_KEY → DeepSeek R1 (chat mejorado, gratis) + Perplexity Sonar (internet, gratis)
ANTHROPIC_API_KEY  → Claude Sonnet 4.5 (conversación premium, de pago, opcional)
GEMINI_API_KEY     → Gemini 2.0 Flash (chat alternativo, gratis 1M tokens/mes)
```

### Por qué OpenRouter en lugar de APIs directas
- Una sola API key para 100+ modelos
- Formato OpenAI-compatible → sin cambios en el código
- Incluye DeepSeek R1 (gratis, calidad top), Perplexity Sonar (gratis, con internet)
- Fácil A/B testing de modelos

### Por qué NO se usa ChatGPT/OpenAI directamente
- De pago desde el primer token
- Groq es ~10x más rápido y gratis
- Para conversación premium → Claude Sonnet 4.5 tiene mejor tono en español

### Acceso a internet (futura)
Dos opciones:
1. **OpenRouter `perplexity/sonar`** — API key, gratis en límites
2. **Perplexica self-hosted** — Docker local, SearxNG, 100% gratis, sin API key

---

## Voz (F15 — futuro)

Groq ya ofrece `whisper-large-v3-turbo` a $0.04/hora.
El flujo es trivial una vez el NLP texto está probado:

```python
# handler de voz
audio_file = await update.message.voice.get_file()
transcription = await groq_client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-large-v3-turbo",
    language="es"
)
# pasar transcription.text a groq_router.route() como texto normal
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

_Creado: 14 abril 2026 — decisiones de arquitectura NLP_
