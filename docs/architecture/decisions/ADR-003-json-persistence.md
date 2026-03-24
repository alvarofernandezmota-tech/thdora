# ADR-003 — JSON como primera capa de persistencia

**Fecha:** 24 marzo 2026  
**Estado:** ✅ Aceptada  
**Autores:** Álvaro Fernández Mota  
**Fase:** Fase 5

---

## Contexto

thdora necesita persistencia de datos (citas y hábitos) que sobreviva al reinicio del proceso. La implementación actual (`MemoryLifeManager`) almacena todo en RAM — los datos se pierden cuando el proceso termina.

Se necesita decidir qué tecnología de persistencia usar en esta fase del proyecto.

---

## Opciones evaluadas

### Opción A — JSON en fichero local ✅ ELEGIDA

**Cómo funciona:** Los datos se serializan a JSON y se guardan en `datos/thdora.json`. Al arrancar, se deserializan.

**Ventajas:**
- Sin dependencias externas (stdlib Python: `json`, `pathlib`)
- Fichero legible por humanos — se puede editar manualmente
- Setup en 0 minutos — no hay servidor que levantar
- Perfecto para un solo usuario en local
- Fácil de hacer backup (copiar el fichero)
- Debugging trivial — abrir el JSON y ver los datos

**Desventajas:**
- No escala a múltiples usuarios
- Sin transacciones — corrupción posible si el proceso muere en medio de una escritura
- Búsquedas lentas con muchos datos (O(n) siempre)
- No es thread-safe sin locking explícito

### Opción B — SQLite

**Ventajas:** Transacciones ACID, búsquedas SQL, thread-safe  
**Desventajas:** Requiere ORM o SQL raw, más complejidad, herramienta nueva en esta fase

### Opción C — SQLAlchemy + PostgreSQL (como thea-ia)

**Ventajas:** Escalable, producción-ready  
**Desventajas:** Requiere servidor PostgreSQL, Alembic para migraciones, mucho overhead para un solo usuario local

---

## Decisión

**JSON en fichero local** para la Fase 5.

### Justificación

1. **thdora es un proyecto personal de un solo usuario** — no necesita la complejidad de una BD relacional ahora
2. **Velocidad de iteración** — implementar `JsonLifeManager` lleva horas, no días
3. **La abstracción ABC ya existe** — cuando necesitemos SQLite o PostgreSQL, solo creamos una nueva implementación sin tocar nada más (Liskov Substitution Principle)
4. **thea-ia ya tiene SQLAlchemy** — cuando thdora lo necesite en el futuro, tenemos el código de referencia en thea-ia
5. **YAGNI** — *You Aren't Gonna Need It*: no añadir complejidad que no se necesita hoy

---

## Consecuencias

### Positivas
- `JsonLifeManager` implementado rápido → bot Telegram puede arrancar antes
- Datos persistentes desde Fase 5 — primera vez que thdora recuerda cosas
- Fichero `datos/thdora.json` en `.gitignore` — datos personales nunca van al repo

### Negativas / Deuda técnica aceptada
- En Fase 10+, cuando necesitemos multiusuario o queries complejas, habrá que migrar a SQLite/PostgreSQL
- El fichero JSON puede corromperse si el proceso muere durante una escritura — aceptable en esta fase

---

## Revisión futura

Revaluar esta decisión cuando:
- thdora necesite más de un usuario
- Las queries de hábitos por rango de fechas sean lentas
- Se implemente sincronización con servidor remoto

---

## Referencias

- [ADR-001](./ADR-001-monorepo.md) — Por qué monorepo
- [ADR-002](./ADR-002-abc-interfaces.md) — Por qué ABC interfaces
- [thea-ia database/](https://github.com/alvarofernandezmota-tech/thea-ia/tree/main/src/theaia/database) — Referencia SQLAlchemy para el futuro
- [MemoryLifeManager](../../../src/core/impl/memory_lifemanager.py) — Implementación base a replicar en JSON
