# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.16.0 (24 abril 2026)

```
Bot Telegram (9 comandos + 5 ConversationHandlers + inline buttons + NLP texto libre)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
    ↕ Groq API (NLP gratuito)
GroqRouter (intent + entidades + chat conversacional + CONTEXTO REAL modo Toki)
```

🟢 **En producción 24/7** en servidor Acer con Docker desde 24 abril 2026.

### Lo que funciona hoy ✅
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar`
- Saludo contextual (buenos días/tardes/noches)
- Navegación ◀️▶️ con fecha real visible en botón central
- Vista detalle de cita con click en ⏰ hora
- Inline buttons: borrar/editar/sumar citas y hábitos
- Conflicto hora en citas: aviso ⚠️ al crear
- `/semana` con navegación semanal y botones por día
- `/config` para configurar tipos de hábitos con botones rápidos
- Fechas flexibles: `hoy`, `mañana`, `ayer`, `27/03`, nombres de día
- **Datos persistentes en SQLite** — sobreviven a reinicios
- **Scheduler F12** — resumen diario + evening log + avisos citas
- **🤖 NLP Groq — modo Toki (v0.14.0):**
  - Contexto real de API inyectado en el prompt (citas + hábitos hoy y mañana)
  - `¿qué tengo hoy?` → responde con datos reales ✅
  - `mañana dentista a las 5` → crea cita ✅
  - `dormí 7 horas` → registra hábito ✅
  - Detección de conflicto de hora ✅
  - Intent `desconocido` → muestra menú del bot ✅
  - 3 llamadas API en paralelo (asyncio.gather)
  - ⏳ Procesando... feedback inmediato al usuario
  - Fix hora 00:00 → pide confirmación antes de crear
  - **Desambiguación borrar/editar** → botones inline cuando hay varias citas candidatas ✅
- **UX borrar cita (v0.16):** confirmación muestra nombre + hora antes de borrar ✅

---

## ✅ Completadas

### F1–F12 — Base, API, Bot, Persistencia, Scheduler
> Ver historial completo en [CHANGELOG.md](CHANGELOG.md)

### F13-base — NLP con Groq ✅ (14 abril 2026)
- Clasificador + extractor entidades + chat conversacional
- Intents: `nueva_cita`, `log_habito`, `consulta`, `chat`, `desconocido`

### F13-toki — Modo Toki: contexto real ✅ (14 abril 2026)
- `api_context` inyectado en el prompt de Groq
- `_build_chat_system()` construye el system prompt con datos reales
- Intent `desconocido` → menú del bot, no texto inventado

### F13-v2a — NLP acciones + desambiguación ✅ (14 abril 2026)
- Cache TTL 2 min con invalidación automática
- Contexto semana completa en borrar/editar
- `nlp_disambig.py` — handler de resolución de cita ambigua con botones inline

### Tarea 1.1 — Desambiguación borrar/editar cita ✅
### Tarea 1.3 — Flujo cancelar cita ✅ (23 abril 2026)
- `cb_apt_delete` muestra nombre + hora antes de confirmación
- Aviso "⚠️ Esta acción no se puede deshacer"
- Degradación elegante si falla la API

---

## 🔶 TRABAJO INMEDIATO — Bloques priorizados

> Un bloque a la vez, en orden.

### 🔴 Bloque 1 — Citas (continuación)

| # | Tarea | Estado |
|---|---|---|
| 1.1 | Desambiguación borrar/editar cita | ✅ Hecho |
| 1.2 | Mostrar horario disponible antes de mover una cita | 🔲 Siguiente |
| 1.3 | Flujo cancelar cita: confirmación + mostrar exactamente qué cita se borra | ✅ Hecho (23-abr) |

### 🟡 Bloque 2 — Menú e interfaz

| # | Tarea | Estado |
|---|---|---|
| 2.1 | Vista semana/días navegable completa desde el menú | 🔲 Pendiente |
| 2.2 | Texto intuitivo y profesional en todos los menús y respuestas | 🔲 Pendiente |
| 2.3 | Consistencia visual — mismo patrón de respuesta en todos los flujos | 🔲 Pendiente |

### 🟠 Bloque 3 — Auditoría y refactoring profesional ← S18 ACTIVO

> Auditado el 27 abril 2026. Plan completo definido.

| # | Tarea | Estado |
|---|---|---|
| 3.1 | Unificar `data/` y `datos/` → una sola carpeta `data/` | 🔲 S18 |
| 3.2 | Mover `COMO_PROCEDER.md` + `AGENTE.md` a `.github/` | 🔲 S18 |
| 3.3 | `docs/`: eliminar `ECOSISTEMA.md` (queda `ECOSYSTEM.md`) | 🔲 S18 |
| 3.4 | `docs/`: fusionar `docs/architecture/` con `ARCHITECTURE.md` | 🔲 S18 |
| 3.5 | `docs/`: mover `diarios/` `sessions/` `auditoria/` fuera de docs pública | 🔲 S18 |
| 3.6 | `docs/`: mover `CLASES_BEGO.md` + `GUIA_BEGO.md` → repo `ejerciciosbego` | 🔲 S18 |
| 3.7 | README profesional — badges + arquitectura + quick start en 3 comandos | 🔲 S18 |
| 3.8 | GitHub Actions CI — workflow pytest en cada push | 🔲 S18–S19 |

### 🔵 Bloque 4 — Multiusuario y despliegue

| # | Tarea | Estado |
|---|---|---|
| 4.1 | Multiusuario — API con `user_id` de Telegram en todos los endpoints | 🔲 Pendiente |
| 4.2 | CD automático — bot siempre corriendo + actualizaciones sin tocar nada | 🔲 Pendiente |
| 4.3 | Beta cerrada — compartir con usuarios cercanos | 🔲 Pendiente |

---

## 🔜 Backlog largo plazo

### F15 — Voz (Whisper)
- [ ] Handler mensajes de voz (`filters.VOICE`)
- [ ] Descargar audio → transcribir con Groq `whisper-large-v3-turbo`
- [ ] Pasar transcripción a `groq_router.route()` como texto normal

### F14 — Tracking personal
- [ ] `sueño`, `sustancias`, `estado`, `estudio`, `proyecto`
- [ ] Tabla `daily_tracking` en SQLite + endpoints CRUD
- [ ] Puntuación diaria (0–10)

### F16–F19 — Gamificación, Mini App, PWA, React Native
- F16: XP + niveles + rachas
- F17: Telegram Mini App
- F18: PWA offline-first
- F19: React Native

---

## Orden recomendado

```
Bloque 1 (Citas) → Bloque 2 (Menú)
    → Bloque 3 (Auditoría profesional) → Bloque 4 (Multi-usuario + CD)
    → F15 (Voz) → F14 (Tracking) → F16–F19 (Apps)
```

---

_Última actualización: 27 abril 2026 — 20:10 CEST — Perplexity AI MCP_
