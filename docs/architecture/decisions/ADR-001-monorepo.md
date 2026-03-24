# ADR-001: Monorepo en lugar de repos separados

**Fecha:** 2026-03-24  
**Estado:** Aceptado

## Contexto

El ecosistema THDORA tenía código distribuido en varios repos:
- `AppointmentManager` — interfaces + implementación core
- `personal/03_proyectos/thdora` — bot CLI y documentación

## Decisión

Unificar todo en el repo `thdora` como **monorepo**.

## Justificación

- ✅ Un solo `git clone` para trabajar en todo el ecosistema
- ✅ Cambios atómicos entre módulos en un solo commit
- ✅ Sin complejidad de versionado entre repos
- ✅ Simplicidad: somos un único desarrollador

## Consecuencias

- `AppointmentManager` queda archivado (se mantiene para historial)
- Todo el desarrollo futuro ocurre en `thdora`
