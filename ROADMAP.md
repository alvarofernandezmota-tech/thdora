# 🗺️ THDORA — ROADMAP

> **Navegación rápida:** [README](README.md) · [Índice docs](docs/INDEX.md) · [CHANGELOG](CHANGELOG.md)

---

## Estado actual — v0.16.4 (14 junio 2026)

```
Bot Telegram (9 comandos + 5 ConversationHandlers + inline buttons + NLP texto libre)
    ↕ httpx async
ThdoraApiClient (9 métodos)
    ↕ FastAPI REST
API (14 endpoints: CRUD + semana + rango + stats)
    ↕ SQLAlchemy ORM
SQLite (data/thdora.db — persistencia real)
    ↕ Groq API (NLP gratuito) — 🟢 OPERATIVO
GroqRouter (intent + entidades + chat conversacional + CONTEXTO REAL modo Toki)
```

🟢 **En producción** en servidor **Madre** (Omarchy, Arch Linux) con Docker desde 14 junio 2026.
> Migrado de Acer → Madre el 14 junio 2026.

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
- **Modelo:** `llama-3.3-70b-versatile` (128k contexto, free tier) — actualizado 14 jun 2026
- **UX borrar cita (v0.16.0):** confirmación muestra nombre + hora antes de borrar ✅
- **Fix B1/B6 (v0.16.1):** emoji 🌆 correcto + cuartos respetan hora seleccionada ✅
- **Fix B-NEW3/B-NEW5/B-NEW6 (v0.16.2):** nombre hábito sin truncar, scheduler fiable, separador noche ✅
- **Tests B-NEW3/B-NEW6/B1 (v0.16.3):** cobertura unit tests añadida ✅
- **Fix Groq 401 + modelo (v0.16.4):** key rotada, modelo actualizado, Git → SSH ✅

---

## ✅ Completadas

### F1–F16 — Base, API, Bot, Persistencia, Scheduler, NLP
> Ver historial completo en [CHANGELOG.md](CHANGELOG.md)

### Tarea 1.1 — Desambiguación borrar/editar cita ✅
### Tarea 1.3 — Flujo cancelar cita ✅ (23 abril 2026)

### Bloque 0 — Infraestructura urgente ✅ RESUELTO (14 junio 2026)

| # | Tarea | Estado |
|---|---|---|
| 0.1 | Renovar GROQ_API_KEY + actualizar modelo | ✅ 14-jun |
| 0.2 | Migrar servidor Acer → Madre (Omarchy) | ✅ 14-jun |
| 0.3 | Git remote HTTPS → SSH | ✅ 14-jun |
| 0.4 | Ejecutar checklist de pruebas en producción | 🔲 Parcial |

### Bloque 3 — Auditoría y refactoring profesional ✅ PARCIAL

| # | Tarea | Estado |
|---|---|---|
| 3.1 | Eliminar carpeta `datos/` vacía | ✅ 27-abr |
| 3.2 | Mover `AGENTE.md` + `COMO_PROCEDER.md` a `.github/` | ✅ 27-abr |
| 3.7 | README profesional | ✅ 27-abr |
| 3.8 | GitHub Actions CI | ✅ 27-abr |

### Bugs resueltos

| ID | Descripción | Fix | Test |
|----|-------------|-----|------|
| B1 | Emoji `🏆` incorrecto franja Tarde | `🌆 Tarde` | ✅ v0.16.3 |
| B6 | `hora_ver_cuartos` mostraba inicio franja | Usa `nueva_hora_temp` | ⚪ handler |
| B-NEW3 | `_kb_edit_hab_fields` truncaba nombre | Nombre completo en callback | ✅ v0.16.3 |
| B-NEW5 | Scheduler no arrancaba (PTB v20+) | `ApplicationBuilder().post_init()` | ⚪ n/a |
| B-NEW6 | Franja noche sin separador visual | Separador `── Madrugada ──` | ✅ v0.16.3 |
| B-SEC1 | GROQ_API_KEY expuesta en canal externo | Key rotada, `.gitignore` verificado | ✅ 14-jun |

---

## 🔶 TRABAJO INMEDIATO — Bloques priorizados

> Un bloque a la vez, en orden.

### 🔴 Bloque 1 — NLP y calidad (SIGUIENTE)

| # | Tarea | Estado |
|---|---|---|
| 1.1 | Fix `TimedOut` al enviar respuesta Telegram desde NLP | 🔲 **SIGUIENTE** |
| 1.2 | Mejorar system prompt — rol claro, límites, contexto | 🔲 Pendiente |
| 1.3 | Pasar contexto dinámico al modelo (citas hoy, hábitos) | 🔲 Pendiente |
| 1.4 | Function calling — crear/borrar citas desde texto libre | 🔲 Pendiente |

### 🟡 Bloque 2 — Citas (continuación)

| # | Tarea | Estado |
|---|---|---|
| 2.1 | Mostrar horario disponible antes de mover una cita | 🔲 Pendiente |
| 2.2 | Vista semana/días navegable completa desde menú | 🔲 Pendiente |

### 🟠 Bloque 3 — Docs y auditoría (resto)

| # | Tarea | Estado |
|---|---|---|
| 3.3 | Eliminar `docs/ECOSISTEMA.md` (duplicado) | 🔲 Pendiente |
| 3.4 | Fusionar `docs/architecture/` con `docs/ARCHITECTURE.md` | 🔲 Pendiente |
| 3.5 | Mover `docs/sessions/` y `docs/auditoria/` fuera de docs pública | 🔲 Pendiente |
| 3.6 | Mover `CLASES_BEGO.md` + `GUIA_BEGO.md` → repo `ejerciciosbego` | 🔲 Pendiente |

### 🔵 Bloque 4 — Multiusuario y despliegue

| # | Tarea | Estado |
|---|---|---|
| 4.1 | Multiusuario — API con `user_id` de Telegram | 🔲 Pendiente |
| 4.2 | CD automático — GitHub Actions deploy a servidor | 🔲 Pendiente |
| 4.3 | Beta cerrada — compartir con usuarios cercanos | 🔲 Pendiente |

### 🟣 Bloque 5 — Infraestructura

| # | Tarea | Estado |
|---|---|---|
| 5.1 | Tailscale en todos los dispositivos | 🔲 Pendiente |
| 5.2 | Script auto-update — despliegue sin SSH manual | 🔲 Pendiente |

---

## 🤖 Visión — Plataforma de Agentes Personales

THDORA es la **plantilla base** de una plataforma de agentes personales. La arquitectura es reutilizable:

```
Docker + FastAPI + SQLite + Bot Telegram + Groq NLP
         ↑
   Cambias solo:
   • System prompt (rol del agente)
   • Endpoints API (qué datos maneja)
   • Handlers bot (flujos de conversación)
```

### Agentes planificados

| Agente | Propósito | Base |
|--------|-----------|------|
| **THDORA** ✅ | Citas, hábitos, salud | Producción |
| Agente gastos | Tickets, presupuesto mensual | THDORA template |
| Agente estudio | Flashcards, progreso | THDORA template |
| Agente trabajo | Tareas, deadlines | THDORA template |
| Bego Bot | Asistente personalizado | THDORA template |

### Mejoras NLP planificadas

| Mejora | Descripción | Prioridad |
|--------|-------------|----------|
| System prompt rico | Rol claro + contexto del usuario + límites | 🔴 Alta |
| Contexto dinámico | Citas del día + hábitos en cada llamada | 🔴 Alta |
| Function calling | Crear/editar/borrar desde texto natural | 🟡 Media |
| Voz (Whisper) | Mensajes de voz transcritos con Groq | 🟢 Baja |
| API del tiempo | Contexto externo (OpenWeatherMap gratuito) | 🟢 Baja |

---

## 🧪 Checklist de pruebas en producción

| Test | Versión | Unit test | Producción |
|------|---------|-----------|------------|
| Flujo /nueva completo con franjas | v0.16.1 | ⚪ parcial | 🔲 Pendiente |
| Emoji 🌆 Tarde correcto (B1) | v0.16.1 | ✅ v0.16.3 | 🔲 Pendiente |
| Cuártos respetan hora seleccionada (B6) | v0.16.1 | ⚪ mock | 🔲 Pendiente |
| Hábito nombre >15 chars editable (B-NEW3) | v0.16.2 | ✅ v0.16.3 | 🔲 Pendiente |
| Separador Madrugada en franja noche (B-NEW6) | v0.16.2 | ✅ v0.16.3 | 🔲 Pendiente |
| Borrar cita muestra nombre+hora | v0.16.0 | ⚪ pendiente | 🔲 Pendiente |
| NLP texto libre (modo Toki) | v0.14.0 | ⚪ mock | 🔲 Pendiente |
| NLP crea cita desde texto | v0.14.0 | ⚪ mock | 🔲 Pendiente |

---

## Orden recomendado

```
Fix TimedOut NLP (1.1)
    → Mejorar system prompt (1.2)
    → Contexto dinámico (1.3)
    → Function calling (1.4)
    → Bloque 2 (citas)
    → Bloque 3 resto (docs)
    → Bloque 4 (multi-usuario)
    → Bloque 5 (infra)
    → Agentes nuevos sobre plantilla THDORA
```

---

_Última actualización: 14 junio 2026 — 23:48 CEST — v0.16.4 — Servidor Madre operativo_
