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
| Arquitectura general | Diagrama de capas, principios de diseño | [`docs/architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) |
| **Mapa del repositorio** | **Dónde está cada cosa y para qué sirve** | [`docs/architecture/repo-map.md`](architecture/repo-map.md) |
| ADR-001 Monorepo | Por qué un solo repo | [`docs/architecture/decisions/ADR-001-monorepo.md`](architecture/decisions/ADR-001-monorepo.md) |
| ADR-002 ABC Interfaces | Por qué interfaces abstractas | [`docs/architecture/decisions/ADR-002-abc-interfaces.md`](architecture/decisions/ADR-002-abc-interfaces.md) |
| ADR-003 JSON Persistence | Por qué JSON como primera persistencia | [`docs/architecture/decisions/ADR-003-json-persistence.md`](architecture/decisions/ADR-003-json-persistence.md) |
| ADR-004 Relación thea-ia | Por qué thdora es independiente de thea-ia | [`docs/architecture/decisions/ADR-004-relacion-thea-ia.md`](architecture/decisions/ADR-004-relacion-thea-ia.md) |

---

## 📦 Módulos

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| core | Interfaces ABC, MemoryLifeManager, JsonLifeManager | [`docs/modules/core.md`](modules/core.md) |
| api | Endpoints FastAPI | [`docs/modules/api.md`](modules/api.md) |

---

## ⚙️ Setup y entorno

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| Entorno local | WSL2 + OpenClaw + Ollama + Telegram + CUDA + PostgreSQL (Fase 11) | [`docs/setup/entorno-local.md`](setup/entorno-local.md) |

---

## 🔍 Auditorías

| Documento | Descripción | Ubicación |
|-----------|-------------|----------|
| Auditoría thea-ia | Inventario completo de módulos y plan de reutilización por fases | [`docs/auditoria/thea-ia.md`](auditoria/thea-ia.md) |

---

## 📅 Diarios técnicos

| Fecha | Horas | Resumen | Enlace |
|-------|-------|---------|--------|
| 2026-03-23 | ~2h | Setup OpenClaw + Ollama + primera conversación Telegram | [`docs/diarios/2026-03-23.md`](diarios/2026-03-23.md) |
| 2026-03-24 | ~4h | Nacimiento repo thdora, arquitectura, 4 ADRs, auditoría thea-ia, repo-map, navegación completa | [`docs/diarios/2026-03-24.md`](diarios/2026-03-24.md) |

---

## 📐 Convenciones

### Nomenclatura de archivos
- Docs de arquitectura: `UPPER_CASE.md` en raíz, `kebab-case.md` en subcarpetas
- ADRs: `ADR-XXX-nombre-decision.md` — numerados en orden cronológico
- Diarios: `YYYY-MM-DD.md` — uno por día trabajado
- Módulos: `nombre-modulo.md` — en minúsculas

### Cuándo crear un ADR
Cada vez que se toma una decisión arquitectónica relevante que afecta al diseño del sistema. Ejemplos: elección de tecnología, patrón de diseño, estructura de datos, relación entre proyectos.

### Cuándo actualizar el diario
Al final de cada día de trabajo en thdora. Documenta **qué** se hizo, **cuánto tiempo** y **por qué**.

### Cuándo actualizar el repo-map
Cada vez que se crea una carpeta nueva o cambia la responsabilidad de un módulo.

### Ecosistema completo

```
alvarofernandezmota-tech/
├── thea-ia          ← proyecto original (intacto, historia)
├── thdora           ← proyecto activo (evolución consciente)
└── personal         ← diario personal y vida
```

---

_Última actualización: 24 marzo 2026 — 21:51 CET_
