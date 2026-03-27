# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.8.0 (27 marzo 2026)

```
Bot Telegram (7 comandos + 4 ConversationHandlers + inline buttons)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
```

**Lo que funciona hoy:**
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/resumen` `/cancelar`
- Inline buttons: borrar/editar citas y hábitos, acumulación `+N`
- Fechas flexibles: `hoy`, `mañana`, `ayer`, `27/03`, nombres de día
- API: 14 endpoints — CRUD + rango + semana + stats + upcoming
- **Datos persistentes en SQLite** — sobreviven a reinicios

---

## ✅ Completadas

### F1–F5 — Base, abstracción, core
- `AbstractLifeManager`, `MemoryLifeManager`, `JsonLifeManager`
- Arquitectura limpia con ADRs

### F6 — FastAPI REST
- Endpoints CRUD para citas y hábitos
- `GET /summary/{date}`

### F7 — Bot Telegram v2
- 5 comandos + `/nueva` 5 pasos + inline buttons
- Fechas flexibles con `dateparser`
- Acumulación `+N` en hábitos
- Fix bug tipo `/nueva` (v2.1)
- Fix contexto acum suelto (v2.1)

### F8 — Endpoints temporales
- `GET /appointments/week/{date}` — citas de la semana
- `GET /appointments/range/{from}/{to}` — citas en rango
- `GET /appointments/upcoming/{date}` — próximas citas
- `GET /habits/week/{date}` — hábitos de la semana
- `GET /habits/range/{from}/{to}` — hábitos en rango
- `GET /habits/stats/{habit}?days=N` — historial hábito
- `GET /summary/week/{date}` — resumen semanal

### F9 — Persistencia SQLite ✅
- `src/db/base.py` — SQLAlchemy engine + `get_session()` + `init_db()`
- `src/db/models.py` — tablas `appointments` + `habits`
- `SQLiteLifeManager` — CRUD completo + rangos + upsert
- Routers migrados: ya no usan `JsonLifeManager`
- `data/thdora.db` — archivo SQLite local

---

## 🔶 En desarrollo — v0.9.x

---

### F9.2 — Hábitos adaptativos + navegación temporal

> **Objetivo:** cada hábito sabe su tipo y se registra con la UI adecuada

#### Nueva tabla `habit_config`
```
habit_config
├── name        → "sueño"
├── type        → numeric | time | boolean | text
├── unit        → "h", "L", "min", ""
├── min_val     → 0
├── max_val     → 24
├── quick_vals  → ["6h","7h","8h","9h"]   ← botones rápidos en el bot
└── xp_rule     → "gte:7"                 ← usado en F10 RPG
```

#### Tipos de hábito

| Tipo | Ejemplos | UI en bot |
|------|----------|-----------|
| `numeric` | humor (1-10), vasos agua | Botones `1`…`10` o `+1 −1` |
| `time` | sueño, ejercicio | Botones `6h` `7h` `8h` o escribe |
| `boolean` | THC, tabaco | Botones `✅ Sí` / `❌ No` |
| `text` | alimentación, notas | Teclado libre |

#### Navegación ◀️▶️
- `/citas` y `/habitos` con botones **Ayer / Hoy / Mañana**
- Inline buttons `[✏️ Editar]` `[🗑️ Borrar]` por cada entrada
- Hábito repetido → aviso con opciones `✏️ Sobreescribir` / `➕ Sumar` / `❌ Cancelar`

#### Conflicto de hora en citas
- Al crear nueva cita: si ya hay una a la misma hora → aviso ⚠️ (no bloquea, solo alerta)

#### Tareas F9.2
- [ ] `src/db/models.py` — nueva tabla `habit_config`
- [ ] `src/core/managers/sqlite_manager.py` — métodos CRUD para `habit_config`
- [ ] `src/api/routers/habit_config.py` — endpoints config
- [ ] `src/bot/handlers.py` — navegación ◀️▶️ en `/citas` y `/habitos`
- [ ] `src/bot/handlers.py` — UI adaptativa según tipo de hábito
- [ ] `src/bot/handlers.py` — detección conflicto de hora al crear cita
- [ ] Tests de `habit_config`

---

### F9.3 — Menú hub + Agenda + Resumen dashboard

> **Objetivo:** THDORA con menú central intuitivo y vista de semana

#### `/menu` — hub principal
```
🏠 THDORA
━━━━━━━━━━━━━━━━
📅 Citas      📊 Hábitos
📋 Resumen    📆 Agenda
🔍 Buscar     ⚙️ Config
```

#### `/resumen` — dashboard diario
```
📋 Viernes 27 marzo
━━━━━━━━━━━━━━━━━━━━━━
📅 CITAS (2)
  22:00 — Cena ✅
📊 HÁBITOS (5/7 registrados)
  ✅ sueño 8h  ✅ ejercicio 30min  ❌ agua
😴 Racha: 3 días  ⭐ XP hoy: +110

[➕ Cita] [📊 Hábito rápido] [📆 Agenda]
```

#### `/agenda` — vista semanal
```
📆 Semana 27 mar → 2 abr
━━━━━━━━━━━━━━━━━━━━━━━
📅 Hoy (vie 27)  → Cena 22:00
📅 Sáb 28        → (sin citas)
📅 Dom 29        → Médico 11:00
[◀️ Anterior] [Siguiente ▶️]
```

#### `/proximas` — próximas 5 citas con cuenta atrás
```
📅 Próximas citas:
  Hoy 22:00 — Cena (en 2h)
  Mañana 10:00 — Dentista (en 12h)
  Dom 11:00 — Médico (en 2 días)
```

#### Tareas F9.3
- [ ] `src/bot/handlers.py` — `/menu` con inline buttons
- [ ] `src/bot/handlers.py` — `/resumen` rediseñado como dashboard
- [ ] `src/bot/handlers.py` — `/agenda` navegación semanal
- [ ] `src/bot/handlers.py` — `/proximas` con cuenta atrás
- [ ] Racha visible en `/habitos`: "🔥 4 días seguidos"

---

### F9.4 — Notificaciones + Exportar + Búsqueda inline

> **Objetivo:** THDORA te habla primero — retención diaria real

#### Notificaciones proactivas
```
notification_config
├── morning_checkin   → 08:00  "Buenos días ☀️ tienes 2 citas hoy"
├── evening_log       → 22:00  "🌙 ¿Cómo fue el día? Registra hábitos"
├── appointment_alert → −30min antes de cada cita
└── cycle_alert       → "🥚 Ovulación mañana"  (si F9.5 activo)
```

#### `/exportar`
- Exporta hábitos del mes a CSV
- Exporta citas del mes a CSV
- Envía el archivo directamente en el chat de Telegram

#### Búsqueda inline
- Filtro dentro de `/citas` y `/habitos` — no comando separado
- Busca en nombre + notas + tipo + fecha

#### `/nota` — diario personal
- Una nota libre por día
- `/nota` → escribe
- `/nota hoy` → leer nota del día

#### Tareas F9.4
- [ ] `src/bot/scheduler.py` — APScheduler para notificaciones
- [ ] `src/db/models.py` — tabla `notification_config`
- [ ] `src/bot/handlers.py` — `/exportar` CSV
- [ ] `src/bot/handlers.py` — búsqueda inline en `/citas` y `/habitos`
- [ ] `src/db/models.py` — tabla `daily_notes`
- [ ] `src/bot/handlers.py` — `/nota`

---

### F9.5 — Ciclo menstrual + Salud física

> **Objetivo:** tracking completo del cuerpo — para ti, tu pareja o quien quieras seguir

#### Ciclo menstrual
```
cycle_config
├── cycle_length        → 28 días (personalizable)
├── period_duration     → 5 días
└── last_period_start   → 2026-03-15

Fases calculadas automáticamente:
  🔴 Menstruación  (días 1-5)
  🌱 Folicular     (días 6-13)   ← energía alta
  🥚 Ovulación     (días 14-16)  ← ventana fértil
  🌕 Lútea         (días 17-28)  ← posible SPM
```

**En el bot:**
```
🌙 Ciclo — hoy día 13
  Fase: 🌱 Folicular
  🥚 Ovulación en 1 día
  Síntomas: [💧Flujo] [😴Cansancio] [😊Bien] [➕ Otro]
```

#### Salud física (`health_log`)
```
├── weight          → kg (numérico)
├── sleep_quality   → ⭐ 1-5 (además de horas)
├── pain            → zona + intensidad 1-10
├── medication      → nombre + dosis + hora
├── blood_pressure  → sistólica / diastólica
└── period_flow     → ligero / medio / abundante
```

#### Tareas F9.5
- [ ] `src/db/models.py` — tablas `cycle_config`, `cycle_log`, `health_log`
- [ ] `src/core/cycle/cycle_engine.py` — cálculo de fases y predicciones
- [ ] `src/api/routers/cycle.py` — endpoints ciclo
- [ ] `src/bot/handlers.py` — `/ciclo` comando
- [ ] `src/bot/handlers.py` — `/salud` comando (peso, tensión, medicación)
- [ ] Notificación automática al acercarse ovulación / próxima regla

---

### F9.6 — Metas (Goals)

> **Objetivo:** objetivos a largo plazo vinculados a hábitos diarios

```
goals
├── title         → "Correr 5km"
├── target        → 5.0
├── unit          → "km"
├── deadline      → 2026-06-01
├── linked_habit  → "ejercicio"   ← cada registro suma automáticamente
└── progress      → 2.3 km (46%)
```

**En el bot:**
```
🎯 Mis metas
━━━━━━━━━━━━━━━━━━━
🏃 Correr 5km
  ████░░░░░░ 46% — queda 2.7km
  📅 Deadline: 1 jun 2026

[➕ Nueva meta] [📊 Ver progreso]
```

#### Tareas F9.6
- [ ] `src/db/models.py` — tabla `goals`
- [ ] `src/core/goals/goal_engine.py` — vinculación hábito → meta
- [ ] `src/api/routers/goals.py` — endpoints CRUD
- [ ] `src/bot/handlers.py` — `/metas` comando

---

## 🔶 F10 — Gamificación RPG

> **Objetivo:** convertir el tracking en un videojuego — se activa cuando ya hay semanas de datos reales

> ⚠️ Esta fase va DESPUÉS de que el sistema esté completo (F9.2–F9.6) para que el RPG tenga datos reales con los que trabajar

### Sistema de XP y niveles

| Hábito | Condición | XP |
|--------|-----------|-----|
| sueño | ≥ 7h | +20 XP |
| ejercicio | cualquier valor | +30 XP |
| estudio | cualquier valor | +40 XP |
| agua | ≥ 2L | +15 XP |
| humor | ≥ 7 | +10 XP |
| sin sustancias | valor = 0 | +50 XP |
| racha 7 días | todos los hábitos | +200 XP bonus |
| meta completada | cualquiera | +500 XP |

> Las reglas de XP se leen desde `habit_config.xp_rule` — no hay que tocar código

**Niveles:**
```
0      XP → 🐣 Novato
500    XP → 📚 Aprendiz
1500   XP → ⚔️  Guerrero
3500   XP → 🧙 Maestro
7500   XP → 👑 Leyenda
```

### Tareas F10
- [ ] `src/db/models.py` — tabla `player_stats` (xp, level, streak, last_update)
- [ ] `src/core/rpg/xp_engine.py` — lee `xp_rule` de `habit_config`
- [ ] `src/core/rpg/level_system.py` — niveles y umbrales
- [ ] `src/core/rpg/streak_tracker.py` — rachas diarias + bonus
- [ ] `src/core/rpg/mission_engine.py` — misiones diarias ("Registra 5 hábitos hoy")
- [ ] `src/api/routers/rpg.py` — `GET /rpg/stats`, `POST /rpg/process/{date}`
- [ ] `src/bot/handlers.py` — `/stats` — nivel, XP, racha, misiones
- [ ] `/resumen` muestra XP del día + barra de nivel
- [ ] Notificación al subir de nivel
- [ ] Tests del motor RPG

---

## ⚪ F11 — IA conversacional + Voz

> **Objetivo:** THDORA entiende lenguaje natural y audio — puedes hablarle y te responde

### Proveedores de IA

| Proveedor | Uso | Modo |
|-----------|-----|------|
| **Groq** (LLaMA / Whisper) | NLP texto + transcripción audio | Cloud rápido |
| **OpenAI** (GPT-4o + Whisper) | NLP avanzado + audio de alta calidad | Cloud premium |
| **Claude** (Anthropic) | Análisis de patrones + resúmenes largos | Cloud analítico |
| **Ollama** (local) | Privacidad total — sin datos fuera | Local offline |

> Arquitectura con provider abstracto — cambias el modelo sin tocar el bot

### Voz bidireccional
```
Tú → 🎤 audio Telegram
       ↓
  Whisper (Groq/OpenAI) → transcripción texto
       ↓
  LLM → interpreta intención
       ↓
  Acción: guarda hábito / crea cita / responde
       ↓
  TTS (opcional) → 🔊 respuesta en audio
```

**Ejemplos reales:**
```
🎤 "Mañana a las diez tengo dentista"
   → ✅ Cita creada: mañana 10:00 — Dentista

🎤 "He dormido siete horas y media y estoy bien"
   → ✅ sueño: 7.5h  ✅ humor: bien

🎤 "¿Cómo llevo el hábito de ejercicio esta semana?"
   → 📊 "Esta semana 4/7 días. Tu mejor racha fue 3 días seguidos"
```

### Comando `/ia` — modo conversación libre
- Preguntas sobre tus datos: "¿Qué día dormí mejor este mes?"
- Análisis de patrones: "¿Hay relación entre mi humor y el sueño?"
- Sugerencias: "Esta semana dormiste menos — ¿quieres ajustar tu alarma?"

### Tareas F11
- [ ] `src/core/ai/provider.py` — clase abstracta `AIProvider`
- [ ] `src/core/ai/groq_provider.py` — Groq (Whisper + LLaMA)
- [ ] `src/core/ai/openai_provider.py` — OpenAI (Whisper + GPT-4o)
- [ ] `src/core/ai/claude_provider.py` — Claude (Anthropic)
- [ ] `src/core/ai/ollama_provider.py` — Ollama local
- [ ] `src/core/ai/intent_parser.py` — extrae intención + entidades del texto
- [ ] `src/core/ai/voice_handler.py` — recibe audio, transcribe, ejecuta
- [ ] `src/bot/handlers.py` — recepción de mensajes de voz (audio)
- [ ] `src/bot/handlers.py` — `/ia` modo conversación libre
- [ ] `src/bot/handlers.py` — `/cr` cita rápida por lenguaje natural
- [ ] Respuesta en audio TTS (opcional, fase 2)
- [ ] Tests del parser de intenciones

---

## ⚪ F12 — Dashboard web

> **Objetivo:** interfaz visual para el historial completo

- [ ] FastAPI + Jinja2 o React
- [ ] Gráficas de hábitos por semana/mes
- [ ] Calendario visual de ciclo menstrual
- [ ] Barra de XP y nivel RPG
- [ ] Progreso de metas
- [ ] Exportar datos a CSV/JSON

---

## ⚪ F13 — Despliegue 24/7

> **Objetivo:** THDORA corriendo siempre, sin intervención manual

- [ ] Docker Compose: `api` + `bot` + volumen `data/`
- [ ] VPS o Raspberry Pi
- [ ] Health checks y reinicio automático
- [ ] Backup automático de `thdora.db`
- [ ] Variables de entorno seguras (`.env` + secrets)

---

## 📊 Visión general de fases

```
F9.2  →  habit_config + tipos adaptativos + navegación ◀️▶️
F9.3  →  /menu + /agenda + /proximas + /resumen hub
F9.4  →  Notificaciones + /exportar + búsqueda + /nota diario
F9.5  →  Ciclo menstrual + salud física (peso, tensión, medicación)
F9.6  →  Metas (goals) vinculadas a hábitos
F10   →  RPG — cuando ya hay semanas de datos reales ✨
F11   →  IA conversacional + voz (Groq / OpenAI / Claude / Ollama)
F12   →  Dashboard web con gráficas
F13   →  Docker + despliegue 24/7
```

---

_Última actualización: 27 marzo 2026 — 22:33 CET_
