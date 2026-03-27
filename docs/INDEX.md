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
│   └── 2026-03-25.md           ← auditoría completa 25-03
├── diarios/
│   ├── 2026-03-23.md
│   ├── 2026-03-24.md
│   ├── 2026-03-25.md
│   └── 2026-03-27.md           ← sesión actual (F7)
├── modules/
│   ├── api.md                  ← módulo FastAPI
│   ├── bot.md                  ← módulo Bot Telegram ← NUEVO
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

## 🚦 Estado del proyecto — 27 marzo 2026

| Módulo | Estado | Cobertura | Versión |
|--------|--------|-----------|----------|
| `src/core/` | ✅ Completo | 100% | 0.6.0 |
| `src/api/` | ✅ Funcional | 87% | 0.6.1 |
| `src/bot/` | ✅ Funcional (mejorable) | — | 0.7.0 |

### Endpoints API disponibles

| Método | Ruta | Estado |
|--------|------|--------|
| GET | `/health` | ✅ |
| GET | `/appointments/{date}` | ✅ |
| POST | `/appointments/{date}` | ✅ |
| DELETE | `/appointments/{date}/{index}` | ✅ |
| GET | `/habits/{date}` | ✅ |
| POST | `/habits/{date}` | ✅ |
| GET | `/summary/{date}` | ✅ |
| PUT | `/appointments/{date}/{index}` | ⏳ Pendiente |
| DELETE | `/habits/{date}/{habit}` | ⏳ Pendiente |
| PUT | `/habits/{date}/{habit}` | ⏳ Pendiente |

---

## 📅 Diarios de sesión

| Fecha | Fase | Logro principal |
|-------|------|-----------------|
| [23 mar](diarios/2026-03-23.md) | F1 | Diseño inicial + ADRs |
| [24 mar](diarios/2026-03-24.md) | F2–F5 | Core + API + tests (61 tests) |
| [25 mar](diarios/2026-03-25.md) | F6 | Summary endpoint + limpieza (87% coverage) |
| [27 mar](diarios/2026-03-27.md) | F7 | Bot Telegram funcional (api_client + handlers + main) |

---

_Última actualización: 27 marzo 2026 — 21:00 CET_
