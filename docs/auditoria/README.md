# 📁 docs/auditoria/

Carpeta de auditorías técnicas del proyecto THDORA.

## ¿Para qué sirve esta carpeta?

Cada vez que se realiza una auditoría del estado del proyecto
(inventario de archivos, revisión de bugs, estado de tests,
deuda técnica pendiente) se crea un documento aquí con:

- Inventario completo de archivos y su estado
- Bugs detectados y corregidos
- Cobertura de tests: qué hay, qué falta
- Plan de trabajo resultante de la auditoría
- Decisión sobre docs desactualizadas o a mover

## Convención de nombres

```
AUDIT-YYYY-MM-DD.md
```

Ejemplo: `AUDIT-2026-04-29.md`

## Auditorías realizadas

| Fecha | Versión | Archivo | Resumen |
|-------|---------|---------|--------|
| 29 abril 2026 | v0.16.2 → v0.16.3 | [AUDIT-2026-04-29.md](AUDIT-2026-04-29.md) | Inventario completo, plan fases 3-7 |

## Cuándo crear una nueva auditoría

- Al acabar un bloque grande de trabajo (cada 3-5 sesiones)
- Antes de un refactoring importante
- Antes de abrir a más usuarios (beta)
- Cuando se sospecha que hay deuda técnica acumulada

---

> **Nota:** Esta carpeta es para documentación interna.
> No es necesario actualizarla en cada sesión.
> Para el seguimiento diario usar `docs/diarios/`.
