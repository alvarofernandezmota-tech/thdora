# 🤖 Stack de IA — Mapa Completo

> _Última actualización: 15 junio 2026_  
> _Documento vivo — actualizar cuando cambien los planes gratuitos_

---

## 🎯 Principio de diseño

**Cada tarea tiene la IA óptima para ella.**  
No usamos una sola IA para todo — diversificamos para maximizar calidad, velocidad y coste cero.

```
Velocidad + gratis   → Groq
Contexto largo       → Gemini
Visión / fotos       → Gemini Vision
Voz entrada          → Groq Whisper
Voz salida básica    → gTTS
Voz salida premium   → ElevenLabs
Código / archivos grandes → Gemini CLI (local)
Fallback offline     → Ollama (local, Madre)
```

---

## 📊 Tabla maestra — IA por tarea

| Tarea | IA óptima | Tier | Límite gratuito | Alternativa |
|---|---|---|---|---|
| **NLP rápido** (intención, entidades) | Groq llama-3.1-8b | ✅ Free | 30 RPM / 14.400 RPD | Ollama local |
| **Respuestas conversacionales** | Groq llama-3.3-70b | ✅ Free | 30 RPM / 14.400 RPD | Gemini 2.5 Flash |
| **Detección mood / journal** | Groq llama-3.3-70b | ✅ Free | mismo | Gemini 2.5 Flash |
| **Resúmenes largos** | Gemini 2.5 Flash | ✅ Free | 10 RPM / 250 RPD | Groq 70b |
| **Contexto muy largo (+100K)** | Gemini 2.5 Pro | ✅ Free | 5 RPM / 100 RPD | Gemini 2.0 Flash |
| **Transcripción de voz** | Groq Whisper | ✅ Free | 30 RPM | OpenAI Whisper |
| **Visión — fotos / pizarras** | Gemini 2.0 Flash | ✅ Free | 15 RPM / 200 RPD | Gemini 2.5 Flash |
| **Voz de salida básica** | gTTS | ✅ Free ilimitado | ∞ | pyttsx3 |
| **Voz de salida premium** | ElevenLabs | 🟡 Pago | ~5€/mes | OpenAI TTS 3€/mes |
| **Embeddings / búsqueda semántica** | Sentence Transformers | ✅ Free local | ∞ | Gemini Embedding |
| **Código + archivos grandes** | Gemini CLI | ✅ Free local | 1M contexto | Claude Code |
| **Fallback offline** | Ollama (Madre) | ✅ Free local | ∞ (local) | — |
| **Function calling** | Groq llama-3.3-70b | ✅ Free | mismo | Gemini 2.5 Flash |

---

## 💰 Límites gratuitos reales (junio 2026)

### Groq API — el corazón del NLP

| Modelo | RPM | TPM | RPD |
|---|---|---|---|
| llama-3.1-8b-instant | 30 | 30.000 | 14.400 |
| llama-3.3-70b-versatile | 30 | 30.000 | 14.400 |
| llama-4-scout | 30 | 30.000 | 14.400 |
| whisper-large-v3 | 30 | — | 14.400 |
| mixtral-8x7b | 30 | 30.000 | 14.400 |

> ⚠️ **Cuando se agota:** error 429 inmediato. Estrategia: TTL cache en `groq_client.py` (ya implementado) + fallback a Ollama local.

**Cuándo deja de ser gratuito:**
- +14.400 peticiones/día por modelo → plan de pago (~$0.05-0.10/1M tokens)
- Con 100 usuarios activos diarios → ~900 req/día → bien dentro del free tier
- Con 1.000 usuarios → considerar plan de pago o Ollama fallback

---

### Gemini API — contexto largo y visión

| Modelo | RPM | TPM | RPD | Contexto |
|---|---|---|---|---|
| Gemini 2.5 Pro | 5 | 250.000 | 100 | 1M tokens |
| Gemini 2.5 Flash | 10 | 250.000 | 250 | 1M tokens |
| Gemini 2.5 Flash-Lite | 15 | 250.000 | 1.000 | 1M tokens |
| Gemini 2.0 Flash | 15 | 1.000.000 | 200 | 1M tokens |
| Gemini 2.5 Flash TTS | 3 | 10.000 | 15 | — |

> ⚠️ **Cuando se agota:** 100 RPD en Gemini Pro es el límite más ajustado. Para resumen semanal y journal: usar 2.5 Flash (250 RPD).

**Cuándo deja de ser gratuito:**
- Gemini 2.5 Pro: con >100 peticiones/día
- Gemini 2.5 Flash: con >250 peticiones/día
- Para THDORA con <50 usuarios: todo gratis
- Para >500 usuarios: $0.075/1M tokens (muy barato)

---

### Voz — entrada y salida

| Servicio | Tipo | Coste | Calidad | Cuándo pagar |
|---|---|---|---|---|
| **Groq Whisper** | STT (entrada) | Gratis | ⭐⭐⭐⭐⭐ | Nunca (dentro del free tier) |
| **gTTS** | TTS (salida) | Gratis ilimitado | ⭐⭐⭐ | Empezar siempre con gTTS |
| **Gemini 2.5 Flash TTS** | TTS | Gratis (15 RPD) | ⭐⭐⭐⭐ | Preview, muy limitado |
| **OpenAI TTS** | TTS | $3/mes | ⭐⭐⭐⭐ | Alternativa barata a ElevenLabs |
| **ElevenLabs** | TTS + voz clonada | ~5-11€/mes | ⭐⭐⭐⭐⭐ | Cuando quieras voz clonada |

---

### Modelos locales — fallback offline (Madre)

| Herramienta | Modelos | Coste | Cuándo usar |
|---|---|---|---|
| **Ollama** | llama3, mistral, phi3 | ✅ Gratis ∞ | Fallback cuando Groq da 429 |
| **Gemini CLI** | Gemini 2.5 Pro (1M ctx) | ✅ Gratis local | Código, auditorías, archivos grandes |
| **Sentence Transformers** | all-MiniLM, etc. | ✅ Gratis local | Búsqueda semántica journal |

---

## 🔄 Estrategia de fallback

```python
# Orden de prioridad en groq_client.py
try:
    respuesta = groq.chat(model="llama-3.1-8b")   # 1º Groq (rápido, gratis)
except RateLimitError:
    respuesta = gemini.chat(model="flash")          # 2º Gemini (gratis, más lento)
except Exception:
    respuesta = ollama.chat(model="llama3")         # 3º Local (offline, ∞)
```

**Esto garantiza que THDORA nunca cae** aunque se agote cualquier API.

---

## 📱 App vs Bot de Telegram/WhatsApp — ¿qué es mejor?

### Comparativa honesta

| Factor | App nativa (iOS/Android) | Bot (Telegram/WhatsApp/Discord) |
|---|---|---|
| **Instalación** | Descargar + registrar | 0 fricción, ya tienes el canal |
| **Coste desarrollo** | 3-6 meses + Swift/Kotlin | Semanas + Python |
| **Notificaciones** | Push nativas, perfectas | Telegram nativas, WA limitadas |
| **Offline** | Puede funcionar parcial | Necesita internet |
| **UX rico** | Botones, gestos, nativo | Limitado a lo que permite el canal |
| **Coste distribución** | Apple 30% + App Store review | ✅ Gratis, sin review |
| **Actualizaciones** | Review 1-3 días | Instantáneo, sin permiso |
| **Adopción** | Hay que convencer de instalar | Ya están en WhatsApp/Telegram |
| **Multiplataforma** | 2 apps (iOS + Android) | 1 bot, todos los dispositivos |
| **Monetización** | In-app purchase, suscripción | Stripe externo |

### Veredicto para THDORA

```
Fase 1 (ahora):   Bot Telegram + WhatsApp
                  → 0 fricción, gratis, llega a todos
                  → Ideal para validar el producto

Fase 2 (v1.0):    Web app (PWA)
                  → Dashboard visual, estadísticas
                  → Complementa el bot, no lo reemplaza

Fase 3 (v2.0):    App nativa SOLO si hay demanda probada
                  → Nunca antes de 1.000 usuarios activos
                  → Coste: ~3-4 meses de desarrollo
```

**Conclusión: el bot siempre primero.** Una app nativa solo tiene sentido cuando tienes usuarios que la piden.

---

## 📦 Diversificación de tareas por IA

```
THDORA en producción — flujo completo:

Usuario escribe texto
    → Groq llama-3.1-8b  (intent parsing, <0.5s)
    → Groq llama-3.3-70b (respuesta Toki, <2s)
    → gTTS si pide audio  (voz salida, gratis)

Usuario envía audio
    → Groq Whisper       (transcripción, <1s)
    → mismo pipeline NLP

Usuario envía foto
    → Gemini 2.0 Flash  (visión, <2s)
    → texto → guardado journal

Resumen semanal (scheduler)
    → Gemini 2.5 Flash  (contexto largo, todos los entries)
    → Enviado por Telegram

Fallback cualquier API
    → Ollama local (Madre, ilimitado, offline)

Código / desarrollo
    → Gemini CLI (Madre, 1M contexto)
    → Mistral Le Chat (archivos grandes en browser)
    → Perplexity MCP  (subir repo, buscar info)
```

---

## ⚠️ Alertas de coste — cuándo pagar

| Situación | Umbral | Acción |
|---|---|---|
| Groq 429 frecuentes | >100 usuarios activos/día | Activar Ollama fallback |
| Gemini RPD agotado | >50 usuarios con journal | Rotar entre Groq + Gemini |
| Voz muy demandada | >200 audios/día | gTTS aguanta, no pagar |
| Escala real | >500 usuarios | Groq pago: ~$5-10/mes |
| App de voz premium | Usuario lo pide | ElevenLabs 5€/mes |

---

_Documento vivo — revisar cada 3 meses o cuando cambien los planes_
