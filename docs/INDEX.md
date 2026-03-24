# Índice de documentación — thdora

> Toda la documentación del proyecto organizada por categoría.  
> Regla: **si no está aquí documentado, no existe.**

---

## 📋 Visión general

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| README | Qué es thdora, cómo arrancarlo | [`/README.md`](/README.md) |
| ROADMAP | Fases del proyecto, estado actual | [`/ROADMAP.md`](/ROADMAP.md) |
| CHANGELOG | Historial de versiones y cambios | [`/CHANGELOG.md`](/CHANGELOG.md) |

---

## 🏗️ Arquitectura

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| Arquitectura general | Diagrama de capas, principios | [`docs/architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) |
| ADR-001 Monorepo | Por qué un solo repo | [`docs/architecture/decisions/ADR-001-monorepo.md`](architecture/decisions/ADR-001-monorepo.md) |
| ADR-002 ABC Interfaces | Por qué interfaces abstractas | [`docs/architecture/decisions/ADR-002-abc-interfaces.md`](architecture/decisions/ADR-002-abc-interfaces.md) |
| ADR-003 JSON Persistence | Por qué JSON como primera persistencia | [`docs/architecture/decisions/ADR-003-json-persistence.md`](architecture/decisions/ADR-003-json-persistence.md) |

---

## 📦 Módulos

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| core | Interfaces ABC, implementaciones | [`docs/modules/core.md`](modules/core.md) |
| api | Endpoints FastAPI | [`docs/modules/api.md`](modules/api.md) |

---

## ⚙️ Setup y entorno

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| Entorno local | WSL2 + OpenClaw + Ollama + Telegram | [`docs/setup/entorno-local.md`](setup/entorno-local.md) |

---

## 🔍 Auditorías

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| Auditoría thea-ia | Inventario y plan de reutilización | [`docs/auditoria/thea-ia.md`](auditoria/thea-ia.md) |

---

## 📅 Diarios técnicos

| Fecha | Resumen | Enlace |
|-------|---------|--------|
| 2026-03-23 | Setup OpenClaw + Ollama + primera conversación Telegram | [`docs/diarios/2026-03-23.md`](diarios/2026-03-23.md) |
| 2026-03-24 | Nacimiento repo thdora, arquitectura, interfaces ABC | [`docs/diarios/2026-03-24.md`](diarios/2026-03-24.md) |

---

## 📐 Convenciones

### Nomenclatura de archivos
- Docs de arquitectura: `UPPER_CASE.md` en raíz, `kebab-case.md` en subcarpetas
- ADRs: `ADR-XXX-nombre-decision.md` — numerados en orden cronológico
- Diarios: `YYYY-MM-DD.md` — uno por día trabajado
- Módulos: `nombre-modulo.md` — en minúsculas

### Cuándo crear un ADR
Cada vez que se toma una decisión arquitectónica relevante que afecta al diseño del sistema y que no es obvia. Ejemplos: elección de tecnología, patrón de diseño, estructura de datos, protocolo de comunicación.

### Cuándo actualizar el diario
Al final de cada día de trabajo en thdora. El diario documenta **qué** se hizo y **por qué** — no es un log de commits.

---

_Última actualización: 24 marzo 2026_
