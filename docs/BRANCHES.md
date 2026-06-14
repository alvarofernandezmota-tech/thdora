# 🌿 GUÍA DE RAMAS — THDORA

> Estado actual de todas las ramas activas y su propósito.

---

## Ramas activas

### `main` — Producción
- **Estado:** ✅ Estable — bot en producción 24/7
- **Regla:** Solo merges probados. NUNCA commits directos sin probar.
- **Contiene:** Bot THDORA v1 completo + documentación maestra

### `feature/agent-platform-v2` — Plataforma v2
- **Estado:** 🔨 En desarrollo activo
- **Objetivo:** Scaffold completo de la plataforma multi-tenant de agentes
- **Base:** Creada desde `main` el 2026-06-15
- **Carpeta principal:** `platform/`
- **Merge a main cuando:** Agent Factory + Tool Registry + Orchestrator probados end-to-end

---

## Convención de nombres

```
feature/nombre-feature   → Nueva funcionalidad
fix/nombre-fix           → Corrección de bug
refactor/nombre          → Refactorización sin cambiar comportamiento
docs/nombre              → Solo documentación
experiment/nombre        → Experimento — puede descartarse
```

---

## Flujo de trabajo

```
experiment/* o feature/*
    ↓ (probado y funcional)
main (producción)
```

**Regla de oro:** Si algo funciona en el bot actual, no se toca hasta
que la nueva versión esté probada en su rama.

---

## Historial de ramas

| Rama | Creada | Estado | Mergeada |
|---|---|---|---|
| `main` | 2026-03-24 | ✅ Activa | — |
| `feature/agent-platform-v2` | 2026-06-15 | 🔨 Activa | Pendiente |
