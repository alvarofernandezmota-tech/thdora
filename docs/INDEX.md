# 📚 THDORA — Índice de documentación

> **Navegación rápida:** [README](../README.md) · [CHANGELOG](../CHANGELOG.md) · [ROADMAP](../ROADMAP.md)

---

## 🗂️ Estructura

```
docs/
├── INDEX.md                    ← este archivo
├── ECOSYSTEM.md                ← visión del ecosistema completo
├── GIT_GUIDE.md                ← flujo de trabajo Git
├── PERSONAL-DATA-PLATFORM.md  ← visión de plataforma de datos
├── architecture/
│   ├── ARCHITECTURE.md         ← arquitectura del sistema
│   └── adr/                    ← decisiones de arquitectura (ADR)
├── auditoria/
│   ├── thea-ia.md              ← relación con Thea IA
│   ├── 2026-03-25.md           ← auditoría completa 25-03
│   └── 2026-03-27.md           ← auditoría sesión F7 v2
├── diarios/
│   ├── 2026-03-23.md
│   ├── 2026-03-24.md
│   ├── 2026-03-25.md
│   └── 2026-03-27.md           ← sesión actual (F7 v2) — CERRADA
├── modules/
│   ├── api.md                  ← módulo FastAPI
│   ├── bot.md                  ← módulo Bot Telegram
│   └── core.md                 ← módulo Core (lógica)
└── setup/
    ├── entorno-local.md        ← setup WSL2 + venv
    └── SETUP.md                ← guía completa instalación
```

---

## 📖 Por dónde empezar

| Si eres... | Empieza por... |
|------------|----------------|
| Nuevo en el proyecto | [README](../README.md) → [ARCHITECTURE](architecture/ARCHITECTURE.md) |
| Configurando el entorno | [SETUP.md](setup/SETUP.md) → [entorno-local.md](setup/entorno-local.md) |
| Trabajando en la API | [modules/api.md](modules/api.md) |
| Trabajando en el bot | [modules/bot.md](modules/bot.md) |
| Trabajando en el core | [modules/core.md](modules/core.md) |
| Revisando historial | [CHANGELOG](../CHANGELOG.md) → [diarios/](diarios/) |
| Viendo el futuro | [ROADMAP](../ROADMAP.md) |

---

## 🚦 Estado del proyecto — v0.7.1 (27 marzo 2026)

| Módulo | Estado | Cobertura | Versión |
|--------|--------|-----------|----------|
| `src/core/` | ✅ Completo | 100% | 0.6.0 |
| `src/api/` | ✅ Funcional | 87% | 0.7.1 |
| `src/bot/` | ✅ Funcional | — | 0.7.1 |

### Endpoints API — estado completo

| Método | Ruta | Estado |
|--------|------|--------|
| GET | `/` (health) | ✅ |
| GET | `/appointments/{date}` | ✅ |
| POST | `/appointments/{date}` | ✅ |
| DELETE | `/appointments/{date}/{index}` | ✅ |
| PUT | `/appointments/{date}/{index}` | ✅ |
| GET | `/habits/{date}` | ✅ |
| POST | `/habits/{date}` | ✅ |
| DELETE | `/habits/{date}/{habit}` | ✅ |
| PUT | `/habits/{date}/{habit}` | ✅ |
| GET | `/summary/{date}` | ✅ |
| GET | `/appointments/upcoming` | ⏳ F8 |
| GET | `/summary/week/{date}` | ⏳ F8 |

### Comandos bot — estado completo

| Comando | Estado | Notas |
|---------|--------|-------|
| `/start` | ✅ | Menú con fechas aceptadas |
| `/citas [fecha]` | ✅ | Inline buttons 🗑️ ✏️ por cita |
| `/nueva` | ⚠️ | 5 pasos — bug: paso tipo se salta |
| `/habitos [fecha]` | ✅ | Inline buttons 🗑️ ✏️ ➕ por hábito |
| `/habito` | ✅ | Teclado + acumulación `+N` |
| `/resumen [fecha]` | ✅ | Citas + hábitos |
| `/cancelar` | ✅ | Aborta cualquier flujo |
| `/agenda` | ⏳ F7 cierre | 7 días con citas |

---

## 🐛 Bugs conocidos (pendientes)

| Bug | Severidad | Fix previsto |
|-----|-----------|-------------|
| `/nueva` salta paso tipo (cita siempre "otra") | 🔴 Alta | Próxima sesión |
| Contexto `acum_hab_nombre` suelto interfiere con `/habitos` | 🟡 Baja | Próxima sesión |

---

## 📅 Diarios de sesión

| Fecha | Fase | Logro principal |
|-------|------|-----------------|
| [23 mar](diarios/2026-03-23.md) | F1 | Diseño inicial + ADRs |
| [24 mar](diarios/2026-03-24.md) | F2–F5 | Core + API + tests (61 tests) |
| [25 mar](diarios/2026-03-25.md) | F6 | Summary endpoint + limpieza (87% coverage) |
| [27 mar](diarios/2026-03-27.md) | F7 | Bot v2: inline buttons, dateparser, acumulación — **CERRADO** |

---

## ⏭️ Próxima sesión (lunes)

1. Fix bug tipo en `/nueva` (30 min)
2. Fix contexto acumulación suelto (10 min)
3. Navegación ◀️ ▶️ en `/citas` y `/habitos`
4. Quitar UUID de mensajes
5. Tests para endpoints PUT/DELETE nuevos
6. `/agenda` — 7 días

---

_Última actualización: 27 marzo 2026 — 21:43 CET_
