# 🚀 Sprint v0.18.0 — Voz + Journal + WhatsApp

> _Siguiente sprint tras merge de v0.17.0 a main_  
> _Última actualización: 15 junio 2026_

---

## 🎯 Objetivo del sprint

Convertir THDORA en un asistente **multi-canal con voz y diario personal** — el primer paso real hacia la visión completa del producto.

```
v0.17.0  ✅ Multi-usuario, NLP v3, 22 tests
    ↓
v0.18.0  🔲 Voz + Journal + WhatsApp
```

---

## 📋 Bloques del sprint (en orden)

### Bloque A — Voz (3-4 días)

| # | Tarea | Dificultad |
|---|---|---|
| A1 | Handler audio en Telegram (voice/audio messages) | Baja |
| A2 | Groq Whisper transcripción → texto | Baja |
| A3 | Conectar transcripción al pipeline NLP existente | Muy baja |
| A4 | Respuesta en audio — gTTS (gratis) | Baja |
| A5 | Respuesta en audio — ElevenLabs (voz clonada, opcional) | Media |

**Stack:**
```python
# Entrada
groq.audio.transcriptions.create(
    file=audio_file,
    model="whisper-large-v3",  # gratis en Groq
    language="es"
)
# Salida
from gtts import gTTS
tts = gTTS(text=respuesta, lang='es')
tts.save("respuesta.ogg")
```

**Recurso open source de referencia:**
- [aviaryan/voice-transcribe-summarize-telegram-bot](https://github.com/aviaryan/voice-transcribe-summarize-telegram-bot) — Groq Whisper + Llama3 en Telegram, Python, MIT
- [bytebone/verbilobot](https://github.com/bytebone/verbilobot) — Telegram + Groq Whisper, referencia de arquitectura audio

---

### Bloque B — Módulo Journal (3-4 días)

| # | Tarea | Dificultad |
|---|---|---|
| B1 | Tabla `journal_entries(user_id, date, text, tags, mood, source)` | Baja |
| B2 | Endpoint API: POST/GET/DELETE entries | Baja |
| B3 | Handler bot: "anota", "reflexión", "idea", "diario" | Baja |
| B4 | Detección automática de mood desde texto (Groq) | Media |
| B5 | Resumen semanal/mensual automático por scheduler | Media |
| B6 | Búsqueda semántica: "¿Qué anoté sobre X?" | Media |
| B7 | Foto → texto (Gemini Vision) | Media |

**Esquema base de datos:**
```sql
CREATE TABLE journal_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    date        DATE NOT NULL,
    text        TEXT NOT NULL,
    tags        TEXT,          -- JSON array: ["idea", "trabajo"]
    mood        TEXT,          -- positivo / neutro / negativo
    source      TEXT,          -- texto / voz / foto
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Ejemplo de uso:**
```
Tú (voz):  "Hoy me sentí muy bien, terminé el proyecto"
Toki:      ✅ Anotado — 15 jun | 😊 Positivo | #personal

Tú:       "¿Qué anoté esta semana?"
Toki:      🗓 Lun: idea proyecto agente voz
            Mar: reunión con cliente bien
            Mie: agotado, poco sueño (patrón detectado ⚠️)
```

---

### Bloque C — WhatsApp (4-5 días)

| # | Tarea | Dificultad |
|---|---|---|
| C1 | Meta WhatsApp Business API setup | Media |
| C2 | Webhook FastAPI para mensajes entrantes | Baja |
| C3 | Adapter WhatsApp → mismo pipeline NLP | Baja |
| C4 | Respuestas: texto + audio + botones (limited) | Media |
| C5 | Tests e2e canal WhatsApp | Media |

**Stack recomendado:**
```python
# Opción A — Meta API directa (gratis hasta 1.000 conv/mes)
pip install requests  # puro HTTP, sin librería extra

# Opción B — Twilio (más fácil de configurar, tiene coste)
pip install twilio

# Opción C — wappa (framework open source WhatsApp)
pip install wappa
```

**Recursos open source de referencia:**
- [wappa](https://pypi.org/project/wappa/) — Framework Python para WhatsApp Business API, arquitectura limpia
- [kaymen99/personal-ai-assistant](https://github.com/kaymen99/personal-ai-assistant) — Multi-canal Telegram+WhatsApp+Slack con agentes, referencia de arquitectura
- [python-whatsapp-bot](https://pypi.org/project/python-whatsapp-bot/) — Cliente WhatsApp Cloud API en Python

---

## 🤖 IA recomendada para cada tarea

| Tarea | IA óptima | Por qué |
|---|---|---|
| **Transcripción de voz** | Groq Whisper | Gratis, <1s, ya tienes la key |
| **NLP / intenciones** | Groq llama-3.1-8b | Ya funciona, ultra rápido |
| **Respuestas complejas** | Groq llama-3.3-70b | Para journal, resumen, análisis |
| **Visión (fotos)** | Gemini 2.0 Flash | 1M contexto, gratis, mejor visión |
| **Voz de salida** | gTTS (gratis) o ElevenLabs | gTTS para empezar, ElevenLabs para voz clonada |
| **Búsqueda semántica journal** | Sentence Transformers | Open source, corre local |
| **Generación código** | Gemini CLI (Madre) | 1M contexto, archivos grandes |

---

## 📦 Repos open source reutilizables

| Repo | Stars | Lo que nos aporta | Licencia |
|---|---|---|---|
| [letta-ai/lettabot](https://github.com/letta-ai/lettabot) | 2k+ | Multi-canal con memoria persistente | MIT |
| [kaymen99/personal-ai-assistant](https://github.com/kaymen99/personal-ai-assistant) | 500+ | Arquitectura multi-canal + agentes | MIT |
| [aviaryan/voice-transcribe-summarize-telegram-bot](https://github.com/aviaryan/voice-transcribe-summarize-telegram-bot) | 300+ | Groq Whisper + Llama3 en Telegram | MIT |
| [bytebone/verbilobot](https://github.com/bytebone/verbilobot) | 200+ | Telegram + Groq Whisper (Go, referencia) | MIT |
| [WAppAI/assistant](https://github.com/WAppAI/assistant) | 400+ | WhatsApp + LLMs | MIT |
| [wappa](https://pypi.org/project/wappa/) | — | Framework WhatsApp Business API Python | MIT |

> ⚠️ **Uso:** Estos repos son de referencia e inspiración. THDORA tiene arquitectura propia — no forkeamos, estudiamos y adaptamos lo mejor de cada uno.

---

## 🗓️ Estimación del sprint

```
Bloque A (Voz)      — 3-4 días
Bloque B (Journal)  — 3-4 días
Bloque C (WhatsApp) — 4-5 días

Total estimado: 10-13 días
Reultado: THDORA v0.18.0 multi-canal con voz y diario
```

---

## ✅ Prerequisito: merge v0.17.0

Antes de empezar este sprint:
```bash
# En Madre:
git pull origin feature/agent-platform-v2
git checkout main
git merge feature/agent-platform-v2 --no-ff -m "merge: v0.17.0"
git push origin main
docker compose down && docker compose up --build -d
pytest tests/ -v  # verificar 22 tests en verde
```

---

_Documento vivo — se actualiza al inicio de cada sprint_
