# 🧠 THDORA — Visión del Producto

> _Última actualización: 15 junio 2026_

---

## ¿Qué es THDORA?

**Tu memoria externa inteligente en el bolsillo.**

No es un chatbot de empresa. No es un asistente genérico. Es un agente personal que **te conoce de verdad** — tu agenda, tu salud, tus hábitos, tus gastos, tus ideas, tu diario — todo conectado, todo tuyo, disponible donde ya estás.

> _"El primer asistente personal que realmente te conoce — vive en tu WhatsApp, corre en tu servidor, y con el tiempo sabe más de ti que cualquier app."_

---

## 🎯 El problema que resuelve

La vida personal está fragmentada en 10 apps que no se hablan:
- Calendario en Google
- Notas en Notion o papel
- Hábitos en otra app
- Gastos en otra
- Diario en otra
- Todo desconectado, todo requiere abrir una app

THDORA lo unifica en **una conversación**, en el canal donde ya estás.

---

## 💡 La propuesta de valor

```
Tú (en el bus, por voz):
"Oye Toki, anota que hoy tuve una idea brutal —
 hacer que el agente recuerde el contexto emocional"

Toki:
"Anotado en ideas del proyecto. ¿Te la recuerdo el lunes?"
```

```
Tú:
"¿Qué tengo esta semana?"

Toki:
📅 Lunes libre
   Miércoles gym 18h
   Jueves médico 10h
   Viernes cena con Ana
   → Llevas 3 días durmiendo poco, ¿necesitas ajustar algo?
```

---

## 🏆 Diferenciadores reales

| Diferenciador | Competencia | THDORA |
|---|---|---|
| **Tus datos son tuyos** | Cloud de empresa | Tu servidor, nadie más los ve |
| **Te conoce con el tiempo** | Reset cada conversación | Historial completo, aprende |
| **Actúa, no solo habla** | Responde preguntas | Crea citas, avisa, documenta |
| **Donde ya estás** | App nueva que instalar | WhatsApp, Telegram, web |
| **Todo conectado** | Apps separadas | Salud + hábitos + diario + gastos |
| **Tu voz, tu idioma** | Interfaz fija | Conversación natural, voz opcional |

---

## 📱 Canales — donde vive el agente

```
                TU AGENTE PERSONAL
                      ↕
          ┌───────────┼───────────┐
     Telegram      WhatsApp    Web Chat
          └───────────┼───────────┘
                      ↕
              FastAPI + SQLite
              (mismo backend)
                      ↕
              Groq NLP (Toki)
```

| Canal | Estado | Prioridad |
|---|---|---|
| **Telegram** | ✅ Producción | — |
| **WhatsApp** | 🔲 Pendiente | v0.18 |
| **Web Chat** | 🔲 Pendiente | v0.19 |
| **Voz (entrada)** | 🔲 Pendiente | v0.18 |
| **Voz (salida)** | 🔲 Pendiente | v0.19 |

---

## 🧩 Módulos del agente

### ✅ Implementados (v0.17.0)
| Módulo | Qué hace |
|---|---|
| **Citas** | Crear, editar, borrar citas con avisos automáticos |
| **Hábitos** | Registrar sueño, agua, ejercicio, cualquier hábito |
| **Agenda semanal** | Vista semana navegable, resumen diario |
| **NLP v3** | Texto libre, modo Toki, intención + entidades |
| **Scheduler** | Resumen mañana, evening log, avisos X min antes |
| **Multi-usuario** | Cada usuario con sus datos separados |

### 🔲 Próximos módulos
| Módulo | Qué hace | Versión |
|---|---|---|
| **Diario / Journal** | Reflexiones, estado de ánimo, ideas, apuntes | v0.18 |
| **Voz** | Groq Whisper entrada + gTTS/ElevenLabs salida | v0.18 |
| **Gastos** | Tickets por foto, presupuesto mensual, alertas | v0.19 |
| **Integraciones** | Google Calendar, Gmail, Notion, GitHub | v0.19 |
| **Resúmenes IA** | Semanal, mensual, tendencias personales | v0.18 |
| **Dashboard web** | Vista visual de todos tus datos | v1.0 |

---

## 🎙️ Stack de voz — arquitectura

```
ENTRADA:
Usuario habla → WhatsApp/Telegram envía audio
    ↓
Groq Whisper API (gratis, <1s)
    ↓
Texto → mismo pipeline NLP de siempre

SALIDA:
Respuesta texto
    ↓
gTTS (gratis) o ElevenLabs (voz clonada)
    ↓
Audio .ogg → Telegram/WhatsApp
```

---

## 📓 Módulo Journal — el killer feature

```
Formatos de entrada:
  Texto:  "Toki, anota..."
  Voz:    🎤 mensaje audio → Whisper → texto
  Foto:   📸 pizarra/libro → Gemini Vision → texto
  Video:  🎥 clase/reunión → transcripción

Lo que Toki hace con eso:
  → Estructura y etiqueta automáticamente
  → Conecta con contexto del día (sueño, estado ánimo)
  → Resumen semanal/mensual automático
  → "Toki, ¿qué anoté sobre X?" → búsqueda semántica
  → Detecta patrones: ideas recurrentes, preocupaciones
```

---

## 🤖 Plataforma multi-agente — la visión grande

THDORA es la **plantilla base**. La arquitectura es reutilizable:

```
Docker + FastAPI + SQLite + Bot Telegram + Groq NLP
         ↑
   Cambias solo:
   • System prompt (rol del agente)
   • Endpoints API (qué datos maneja)
   • Handlers bot (flujos de conversación)
         ↓
   Nuevo agente en 2-4 horas
```

### Agentes planificados

| Agente | Para quién | Qué hace |
|---|---|---|
| **THDORA** ✅ | Personal | Salud, citas, hábitos, diario |
| **Agente gastos** | Cualquiera | Tickets, presupuesto, alertas |
| **Agente estudio** | Estudiantes | Flashcards, progreso, exámenes |
| **Agente trabajo** | Profesionales | Tareas, deadlines, reuniones |
| **Agente empresa** | Negocios | CRM ligero, seguimiento clientes |
| **Bego Bot** | Personalizado | Asistente a medida |

---

## 💼 Modelo de negocio

```
"Te instalo tu agente personal en 24h"

Planes:
  Básico  — 9€/mes  — 1 agente, Telegram
  Pro     — 19€/mes — Multi-canal (WhatsApp + Web)
  Premium — 49€/mes — Agente personalizado + voz clonada
  B2B     — custom  — Agente para tu empresa/equipo
```

**Moat:** el usuario no se va nunca — perdería años de contexto personal acumulado.

---

## 🗺️ Roadmap de versiones

```
v0.17.0  ✅ HOY    MVP multi-usuario, NLP v3, 22 tests
v0.18.0  → Sprint 1  Voz (Whisper) + Journal + WhatsApp
v0.19.0  → Sprint 2  Gastos + Google Calendar + Web chat
v1.0.0   → Sprint 3  Dashboard + plataforma multi-agente
v2.0.0   → Futuro    Fine-tuning personalizado por usuario
```

---

_Documento vivo — se actualiza con cada sprint_
