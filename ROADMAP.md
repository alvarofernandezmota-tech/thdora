# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.16.3 (29 abril 2026)

```
Bot Telegram (9 comandos + 5 ConversationHandlers + inline buttons + NLP texto libre)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
    ↕ Groq API (NLP gratuito) — 🔴 KEY EXPIRADA
GroqRouter (intent + entidades + chat conversacional + CONTEXTO REAL modo Toki)
```

🟢 **En producción 24/7** en servidor Acer con Docker desde 24 abril 2026.

### Lo que funciona hoy ✅
- `/start` `/citas` `/habitos` `/habito` `/nueva` `/semana` `/resumen` `/config` `/cancelar`
- Saludo contextual (buenos días/tardes/noches)
- Navegación ◀️▶️ con fecha real visible en botón central
- Vista detalle de cita con click en ⏰ hora
- Inline buttons: borrar/editar/sumar citas y hábitos
- Conflicto hora en citas: aviso ⚠️ al crear y al editar
- `/semana` con navegación semanal y botones por día
- `/config` para configurar tipos de hábitos con botones rápidos
- Fechas flexibles: `hoy`, `mañana`, `ayer`, `27/03`, nombres de día
- **Datos persistentes en SQLite** — sobreviven a reinicios
- **Scheduler F12** — resumen diario + evening log + avisos citas
- **🤖 NLP Groq — modo Toki (v0.14.0)** — contexto real, crea citas/hábitos, desambiguación
- **UX borrar cita (v0.16.0):** confirmación muestra nombre + hora antes de borrar ✅
- **Fix B1/B6 (v0.16.1):** emoji 🌆 correcto + cuartos respetan hora seleccionada ✅
- **Fix B-NEW3/B-NEW5/B-NEW6 (v0.16.2):** nombre hábito sin truncar, scheduler fiable, separador noche ✅
- **Tests B-NEW3/B-NEW6/B1 (v0.16.3):** cobertura unit tests añadida ✅

---

## ✅ Completadas

### F1–F16 — Base, API, Bot, Persistencia, Scheduler, NLP
> Ver historial completo en [CHANGELOG.md](CHANGELOG.md)

### Tarea 1.1 — Desambiguación borrar/editar cita ✅
### Tarea 1.3 — Flujo cancelar cita ✅ (23 abril 2026)

### Bloque 3 — Auditoría y refactoring profesional ✅ PARCIAL (27 abril 2026)

| # | Tarea | Estado |
|---|---|---|
| 3.1 | Eliminar carpeta `datos/` vacía — `data/` única fuente de datos | ✅ 27-abr |
| 3.2 | Mover `AGENTE.md` + `COMO_PROCEDER.md` a `.github/` | ✅ 27-abr |
| 3.7 | README profesional — v0.16.0, quick start, arquitectura real | ✅ 27-abr |
| 3.8 | GitHub Actions CI — fix Python 3.12 + cache pip | ✅ 27-abr |

### Bugs resueltos (historial)

| ID | Descripción | Fix | Test unitario |
|----|-------------|-----|--------------|
| B1 | Emoji `🏆` incorrecto en franja Tarde | `🌆 Tarde` — consistente con `_kb_franjas()` | ✅ v0.16.3 |
| B6 | `hora_ver_cuartos` mostraba inicio de franja | Usa `nueva_hora_temp` si existe | ⚪ handler (mock complejo) |
| B8 | Pattern `^quick_nueva` analizado | No era bug — cerrado sin cambios | n/a |
| B-NEW3 | `_kb_edit_hab_fields` truncaba nombre ([:15]) | Nombre completo en callback_data | ✅ v0.16.3 |
| B-NEW5 | Scheduler no arrancaba (PTB v20+ post_init) | `ApplicationBuilder().post_init()` | ⚪ no aplica (main.py) |
| B-NEW6 | Franja noche sin separador visual 22-23/00-05 | Separador `── Madrugada ──` | ✅ v0.16.3 |

---

## 🔶 TRABAJO INMEDIATO — Bloques priorizados

> Un bloque a la vez, en orden.

### 📙 Bloque 0 — Infraestructura urgente

| # | Tarea | Estado |
|---|---|---|
| 0.1 | Renovar GROQ_API_KEY en `.env` del servidor Acer | 🔴 **URGENTE — NLP bloqueado** |
| 0.2 | Ejecutar checklist de pruebas en producción (Telegram real) | 🔲 Tras renovar key |

### 🔴 Bloque 1 — Citas (continuación)

| # | Tarea | Estado |
|---|---|---|
| 1.1 | Desambiguación borrar/editar cita | ✅ Hecho |
| 1.2 | Mostrar horario disponible antes de mover una cita | 🔲 **SIGUIENTE** |
| 1.3 | Flujo cancelar cita: confirmación + mostrar exactamente qué cita se borra | ✅ Hecho (23-abr) |

### 🟡 Bloque 2 — Menú e interfaz

| # | Tarea | Estado |
|---|---|---|
| 2.1 | Vista semana/días navegable completa desde el menú | 🔲 Pendiente |
| 2.2 | Texto intuitivo y profesional en todos los menús y respuestas | 🔲 Pendiente |
| 2.3 | Consistencia visual — mismo patrón de respuesta en todos los flujos | 🔲 Pendiente |

### 🟠 Bloque 3 — Auditoría y refactoring profesional

| # | Tarea | Estado |
|---|---|---|
| 3.1 | Eliminar `datos/` vacía | ✅ 27-abr |
| 3.2 | Mover `AGENTE.md` + `COMO_PROCEDER.md` a `.github/` | ✅ 27-abr |
| 3.3 | Eliminar `docs/ECOSISTEMA.md` (duplicado de `ECOSYSTEM.md`) | 🔲 S18 |
| 3.4 | Fusionar `docs/architecture/` con `docs/ARCHITECTURE.md` | 🔲 S18 |
| 3.5 | Mover `docs/sessions/` y `docs/auditoria/` fuera de docs pública | 🔲 S18 |
| 3.6 | Mover `CLASES_BEGO.md` + `GUIA_BEGO.md` → repo `ejerciciosbego` | 🔲 S18 |
| 3.7 | README profesional | ✅ 27-abr |
| 3.8 | GitHub Actions CI — pytest en cada push | ✅ 27-abr |

### 🔵 Bloque 4 — Multiusuario y despliegue

| # | Tarea | Estado |
|---|---|---|
| 4.1 | Multiusuario — API con `user_id` de Telegram | 🔲 Pendiente |
| 4.2 | CD automático — GitHub Actions deploy a servidor | 🔲 Pendiente |
| 4.3 | Beta cerrada — compartir con usuarios cercanos | 🔲 Pendiente |

### 🟣 Bloque 5 — Infraestructura

| # | Tarea | Estado |
|---|---|---|
| 5.1 | Instalar Tailscale en Acer + móvil + PC | 🔲 S18 |
| 5.2 | Renovar GROQ_API_KEY — desbloquea NLP completo | 🔴 **URGENTE** |
| 5.3 | Script auto-update — despliegue sin SSH manual | 🔲 S18–S19 |

---

## 🧪 Checklist de pruebas en producción

> Pendiente ejecutar en el bot real (Telegram + Acer). Todos los fixes están en código.
> Tests unitarios ✅ — pruebas manuales en producción pendientes.

| Test | Versión | Unit test | Producción |
|------|---------|-----------|------------|
| Flujo /nueva completo con franjas | v0.16.1 | ⚪ parcial | 🔲 Pendiente |
| Emoji 🌆 Tarde correcto (B1) | v0.16.1 | ✅ v0.16.3 | 🔲 Pendiente |
| Cuartos respetan hora seleccionada (B6) | v0.16.1 | ⚪ mock complejo | 🔲 Pendiente |
| Hábito nombre >15 chars editable (B-NEW3) | v0.16.2 | ✅ v0.16.3 | 🔲 Pendiente |
| Separador Madrugada en franja noche (B-NEW6) | v0.16.2 | ✅ v0.16.3 | 🔲 Pendiente |
| Borrar cita muestra nombre+hora | v0.16.0 | ⚪ pendiente | 🔲 Pendiente |
| Conflicto hora en /nueva | v0.15.1 | ✅ overlap | 🔲 Pendiente |
| Conflicto hora en editar | v0.15.1 | ⚪ handler | 🔲 Pendiente |
| Scheduler /start arranca (B-NEW5) | v0.16.2 | ⚪ no aplica | 🔲 Pendiente |
| NLP texto libre | v0.14.0 | ⚪ Groq mock | 🔴 BLOQUEADO (Groq key) |

---

## 🔜 Backlog largo plazo

### F15 — Voz (Whisper)
- [ ] Handler mensajes de voz (`filters.VOICE`)
- [ ] Transcribir con Groq `whisper-large-v3-turbo`

### F14 — Tracking personal
- [ ] `sueño`, `sustancias`, `estado`, `estudio`, `proyecto`
- [ ] Tabla `daily_tracking` en SQLite + endpoints CRUD

### F16–F19 — Gamificación, Mini App, PWA, React Native

---

## Orden recomendado

```
Bloque 0.1 (Groq key) → Bloque 0.2 (tests producción)
    → Bloque 1.2 (citas huecos) → Bloque 2 (Menú)
    → Bloque 3 resto (docs) → Bloque 5.1 (Tailscale)
    → Bloque 4 (Multi-usuario) → F15 (Voz) → F14 (Tracking)
    → F16–F19 (Apps)
```

---

_Última actualización: 29 abril 2026 — 21:50 CEST — v0.16.3 + tests unit completos_
