# 🗂️ THDORA — Índice de documentación

> **Navegación:** [README](../README.md) · [ROADMAP](../ROADMAP.md) · [CHANGELOG](../CHANGELOG.md) · [Cómo proceder](../COMO_PROCEDER.md)

---

## Documentación principal (raíz del repo)

| Fichero | Contenido |
|---|---|
| [README.md](../README.md) | Descripción del proyecto, funcionalidades, arranque rápido, estructura, portfolio |
| [COMO_PROCEDER.md](../COMO_PROCEDER.md) | Estado actual, cómo arrancar, convenciones, siguiente paso |
| [ROADMAP.md](../ROADMAP.md) | Hoja de ruta completa F1 → F18 con estado de cada feature |
| [CHANGELOG.md](../CHANGELOG.md) | Historial de versiones con cambios detallados (v0.1 → v0.15.1) |

---

## Documentación técnica (`docs/`)

| Fichero | Contenido |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | ⭐ Arquitectura del sistema, descripción de cada módulo y fichero, decisiones de diseño |
| [FLUJOS_DETALLADOS.md](FLUJOS_DETALLADOS.md) | ⭐ Flujos internos del bot: estados, transiciones, casos borde, acumulación |
| [API_REFERENCE.md](API_REFERENCE.md) | ⭐ Referencia completa de todos los endpoints REST con ejemplos |
| [CONVENCIONES.md](CONVENCIONES.md) | ⭐ Patrones callback_data, variables de entorno, convenciones de código y commits |
| [NLP_ARQUITECTURA.md](NLP_ARQUITECTURA.md) | ⭐ Arquitectura del módulo NLP/IA: modelos, intents, conflicto, contexto real, roadmap IA |
| [F12_NOTIFICACIONES_DESIGN.md](F12_NOTIFICACIONES_DESIGN.md) | Diseño completo de la feature de notificaciones proactivas |
| [ECOSYSTEM.md](ECOSYSTEM.md) | Visión del ecosistema completo (bot, API, DB, futuro) |
| [GIT_GUIDE.md](GIT_GUIDE.md) | Guía de flujo de trabajo con Git |

---

## Directorios

| Directorio | Contenido |
|---|---|
| `docs/architecture/` | ADRs (Architecture Decision Records) — decisiones importantes documentadas |
| `docs/diarios/` | Diarios de sesión de desarrollo |
| `docs/sessions/` | Resumen de sesiones de trabajo |
| `docs/modules/` | Documentación específica de módulos |
| `docs/setup/` | Guías de configuración del entorno |
| `docs/auditoria/` | Auditorías de código y estado del repo |

---

## Mapa de lectura según rol

### 👔 Reclutador / tech lead
1. [README.md](../README.md) — qué es y por qué es un buen portfolio
2. [ARCHITECTURE.md](ARCHITECTURE.md) — decisiones técnicas
3. [CHANGELOG.md](../CHANGELOG.md) — evolución del proyecto (v0.1 → v0.15.1)
4. [ROADMAP.md](../ROADMAP.md) — visión y próximos pasos

### 🧑‍💻 Desarrollador que quiere contribuir
1. [COMO_PROCEDER.md](../COMO_PROCEDER.md) — arranca aquí
2. [CONVENCIONES.md](CONVENCIONES.md) — reglas del proyecto
3. [FLUJOS_DETALLADOS.md](FLUJOS_DETALLADOS.md) — cómo funciona cada flujo
4. [API_REFERENCE.md](API_REFERENCE.md) — endpoints disponibles
5. [NLP_ARQUITECTURA.md](NLP_ARQUITECTURA.md) — cómo funciona la IA

### 🔍 Auditoría / revisión de código
1. [ARCHITECTURE.md](ARCHITECTURE.md) — estructura
2. [CONVENCIONES.md](CONVENCIONES.md) — patrones y convenciones
3. [FLUJOS_DETALLADOS.md](FLUJOS_DETALLADOS.md) — comportamiento esperado
4. [NLP_ARQUITECTURA.md](NLP_ARQUITECTURA.md) — lógica de intents y conflictos

---

_Última actualización: 14 abril 2026 — 18:32 CEST_
