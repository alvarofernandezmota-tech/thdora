# 📓 Diario de Bolsillo — Nueva Focalización del Producto

> _Documento creado: 15 junio 2026_  
> _Rama: feature/agent-platform-v2_

---

## 💡 La idea central

**"Tu diario inteligente en el bolsillo — siempre contigo, en todos los canales donde ya estás."**

No es una app de notas. No es un chatbot de empresa. Es un **asistente personal que te escucha, organiza tu vida y te la devuelve cuando la necesitas** — por texto, por voz, por foto.

```
Tú (en el bus, por voz):
"Óye Toki, anota que hoy tuve una idea: hacer que el agente
recuerde cómo me sentí cada día y conecte eso con mis hábitos"

Toki:
✅ Anotado — 15 jun | 😊 Positivo | #idea #proyecto
🔔 ¿Te la recuerdo el lunes por la mañana?
```

---

## 📱 Dónde vive el agente — canales

### 🟢 Gratuitos o casi gratuitos

| Canal | Coste | Facilidad | Prioridad |
|---|---|---|---|
| **Telegram** | ✅ Gratis, siempre | ✅ Ya funciona | HOY |
| **Discord** | ✅ Gratis | ✅ Fácil (discord.py) | Sprint 2 |
| **Web Chat** | ✅ Gratis (self-hosted) | ✅ Fácil (WebSocket) | Sprint 2 |
| **CLI / Terminal** | ✅ Gratis | ✅ Muy fácil | Sprint 2 |
| **Obsidian plugin** | ✅ Gratis | Media | Sprint 3 |

### 🟡 WhatsApp — la realidad de costes

> **El API de WhatsApp (Meta Cloud API) es GRATIS de acceder.**  
> Lo que cuesta son los mensajes que TÚ mandas primero (outbound).

| Tipo mensaje | Coste (ES/EU) | Cuándo |
|---|---|---|
| **Service** (usuario escribe primero) | **€0.00 GRATIS** | Siempre, ventana 24h |
| **Utility** (confirmaciones, avisos) | ~€0.07/msg | Si tú inicias |
| **Marketing** (promos) | ~€0.13/msg | Si tú inicias |

**Conclusión para THDORA:**
- Si el usuario escribe primero → **gratis ilimitado**
- Resumen diario automático (tú lo envías) → ~€0.07/usuario/día → ~€2.10/usuario/mes
- Con 100 usuarios: ~210€/mes solo en WhatsApp notifications
- **Estrategia:** en WhatsApp el usuario siempre escribe primero — los resúmenes por Telegram

### 🟠 Canales futuros

| Canal | Coste | Dificultad | Cuándo |
|---|---|---|---|
| **WhatsApp** | Gratis si inbound | Media | Sprint 1 |
| **Instagram DM** | Gratis (Meta Graph API) | Media | v1.0 |
| **Slack** | Gratis (tier free) | Fácil | v1.0 |
| **iMessage** | Solo Mac, complejo | Alta | v2.0 |
| **SMS** | Twilio ~0.01€/sms | Media | v2.0 |

---

## 📓 El Módulo Diario — arquitectura completa

### Formatos de entrada

```
Texto:    "Toki, anota..."           → directo
Voz:      🎤 audio message            → Groq Whisper → texto
Foto:     📸 pizarra / libro / ticket  → Gemini Vision → texto
Video:    🎥 clase / reunión           → Whisper → transcripción
```

### Lo que Toki hace automáticamente

```
1. Estructura y etiqueta (idea / reflexión / tarea / apunte)
2. Detecta estado de ánimo desde el texto (Groq)
3. Conecta con contexto del día (sueño, hábitos, citas)
4. Guarda con fecha, hora, canal origen
5. Resumen semanal/mensual automático
6. Búsqueda: "¿Qué anoté sobre X?" → búsqueda semántica
7. Detecta patrones: ideas recurrentes, preocupaciones
```

### Esquema base de datos

```sql
CREATE TABLE journal_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    date        DATE NOT NULL,
    text        TEXT NOT NULL,
    tags        TEXT,        -- JSON: ["idea","trabajo","personal"]
    mood        TEXT,        -- positivo / neutro / negativo
    source      TEXT,        -- texto / voz / foto / video
    channel     TEXT,        -- telegram / whatsapp / discord / web
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Ejemplos de uso real

```
— APUNTE RÁPIDO —
Tú:    "Idea: integrar Google Fit para pasos automáticos"
Toki:  ✅ Idea guardada | #producto #integraciones

— REFLEXIÓN —
Tú:    "Hoy estoy agotado, no sé si voy bien con el proyecto"
Toki:  Anotado 😔 | Llevas 3 días con estado bajo — ¿necesitas parar?

— APUNTE DE CLASE / REUNIÓN —
Tú:    📸 [foto pizarra]
Toki:  Texto extraído y guardado: "Arquitectura microservicios..."

— BÚQUEDA —
Tú:    "¿Qué anoté sobre WhatsApp?"
Toki:  🗋 3 entradas encontradas:
        12 jun: "WhatsApp cuesta 0.07€ si enviamos nosotros"
        14 jun: "Meta API gratis si el usuario escribe primero"
        15 jun: "Estrategia: resúmenes por Telegram, WA solo inbound"

— RESUMEN SEMANAL (automático) —
Toki:  🗓 Semana 9-15 jun:
        5 ideas anotadas (3 sobre el producto)
        Estado: positivo 4 días, neutro 2, bajo 1
        Tendencia: productividad alta Ma-Jue
        Pendiente revisar: integración Google Calendar
```

---

## 🤖 IA óptima por tarea

| Tarea | IA | Coste | Velocidad |
|---|---|---|---|
| Transcripción voz | **Groq Whisper** | Gratis | <1s |
| Detección intención / tags | **Groq llama-3.1-8b** | Gratis | <0.5s |
| Detección mood + resumen | **Groq llama-3.3-70b** | Gratis | <2s |
| Visión (fotos/pizarras) | **Gemini 2.0 Flash** | Gratis | <2s |
| Búsqueda semántica | **Sentence Transformers** | Gratis (local) | <0.3s |
| Voz de salida básica | **gTTS** | Gratis | <1s |
| Voz de salida premium | **ElevenLabs** | ~5€/mes | <1s |
| Código / archivos grandes | **Gemini CLI (Madre)** | Gratis | — |

---

## 📦 Repos open source de referencia

### Voz
| Repo | Qué reutilizar | Licencia |
|---|---|---|
| [aviaryan/voice-transcribe-summarize-telegram-bot](https://github.com/aviaryan/voice-transcribe-summarize-telegram-bot) | Handler audio PTB + llamada Groq Whisper | MIT |
| [bytebone/verbilobot](https://github.com/bytebone/verbilobot) | Arquitectura Telegram + Groq Whisper (Go, referencia) | MIT |

### Multi-canal
| Repo | Qué reutilizar | Licencia |
|---|---|---|
| [kaymen99/personal-ai-assistant](https://github.com/kaymen99/personal-ai-assistant) | Adaptadores multi-canal (Telegram+WA+Slack), arquitectura agentes | MIT |
| [letta-ai/lettabot](https://github.com/letta-ai/lettabot) | Memoria persistente multi-canal, referencia arquitectura | MIT |
| [janbanot/personal_assistant](https://github.com/janbanot/personal_assistant) | Asistente personal CLI + Discord, arquitectura limpia | MIT |

### WhatsApp
| Repo / Librería | Qué usar | Licencia |
|---|---|---|
| [python-whatsapp-bot](https://pypi.org/project/python-whatsapp-bot/) | Cliente Python para Meta Cloud API | MIT |
| [wappa](https://pypi.org/project/wappa/) | Framework WhatsApp workflows + agentes | MIT |
| [WAppAI/assistant](https://github.com/WAppAI/assistant) | WhatsApp + LLMs, referencia webhook | MIT |

### Discord
| Repo | Qué usar | Licencia |
|---|---|---|
| discord.py (oficial) | Librería Python Discord Bot | MIT |
| [janbanot/personal_assistant](https://github.com/janbanot/personal_assistant) | Bot Discord + AI, arquitectura adaptable | MIT |

> ⚠️ **Uso:** Todos son de referencia e inspiración. THDORA tiene arquitectura propia.

---

## 🗺️ Roadmap actualizado con foco Diario

```
v0.17.0  ✅ HOY     MVP: citas, hábitos, NLP v3, multi-user
v0.18.0  🔲 Sprint1  Voz + Diario/Journal + WhatsApp
v0.19.0  🔲 Sprint2  Gastos + Google Calendar + Discord + Web
v1.0.0   🔲 Sprint3  Dashboard + plataforma multi-agente
v2.0.0   🔲 Futuro   Fine-tuning personalizado, voz clonada
```

### Orden de canales por impacto/esfuerzo

```
1. Telegram   ✅ YA FUNCIONA
2. Discord    — 3 días (discord.py, mismo backend)
3. WhatsApp   — 5 días (Meta API gratis si inbound)
4. Web Chat   — 4 días (WebSocket + widget JS)
5. Slack      — 3 días (Bolt SDK Python)
```

---

## 💼 Modelo de negocio ajustado

```
Tier Free:     Telegram — 1 agente, sin voz
Tier Basic:    9€/mes — + WhatsApp + Voz básica
Tier Pro:      19€/mes — + Discord + Web + Diario completo
Tier Premium:  49€/mes — Voz clonada + todos los canales
Tier B2B:      custom  — Agente para empresa/equipo
```

**Nota WhatsApp:** incluir ~2€/usuario/mes de coste WhatsApp en tiers Basic+

---

## ✅ Resumen ejecutivo — qué hacemos ahora

```
HOY:      Merge v0.17.0 a main (falta keyboards.py)
Sprint 1: Voz (Groq Whisper) — 3-4 días
Sprint 1: Diario/Journal    — 3-4 días  
Sprint 1: WhatsApp           — 5 días
Sprint 2: Discord            — 3 días
```

**El foco del producto: "Tu diario inteligente de bolsillo, en todos los canales donde ya estás."**

---

_Documento vivo — actualizar al inicio de cada sprint_
