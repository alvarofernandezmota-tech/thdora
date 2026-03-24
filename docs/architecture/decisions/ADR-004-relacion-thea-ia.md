# ADR-004 — Relación entre thdora y thea-ia

**Fecha:** 24 marzo 2026  
**Estado:** ✅ Aceptada  
**Autores:** Álvaro Fernández Mota  

---

## Contexto

`thea-ia` es el proyecto original: 6+ meses de trabajo construyendo un sistema conversacional de IA desde cero, sin una arquitectura definida de antemano, persiguiendo una visión. Contiene un bot de Telegram implementado, un motor NLP, un orquestador, un router, gestores de conversación, sistema multi-agente, base de datos real con SQLAlchemy + Alembic y deploy en Railway.

`thdora` nace el 24 de marzo de 2026 con una arquitectura limpia, documentación profesional desde el día 1 y una visión clara: asistente personal con OpenClaw + Ollama local + bot Telegram + gestión de vida.

Había que decidir cómo se relacionan estos dos proyectos.

---

## Opciones evaluadas

### Opción A — thdora absorbe thea-ia módulo a módulo ✅ ELEGIDA

thdora es el repo principal y el proyecto activo. thea-ia se mantiene intacto como referencia histórica y cantera de código. Cada vez que thdora necesita implementar algo que ya existe en thea-ia, se lee el módulo correspondiente, se entiende cómo se resolvió antes, y se reescribe mejor con la arquitectura limpia de thdora.

### Opción B — thdora como módulo dentro de thea-ia

thdora se integra como `src/theaia/life_manager/` dentro del repo de thea-ia, heredando toda la infraestructura existente.

---

## Decisión

**Opción A.** thdora es el proyecto principal. thea-ia queda intacto.

### Justificación

1. **thea-ia fue construido sin visión clara** — el código es real y funcional, pero arrastra decisiones tomadas sin criterio. Copiarlo en bloque a thdora heredaría esa deuda técnica.

2. **Reescribir con criterio es mejor que copiar** — cuando lleguemos a la Fase 7 (bot Telegram), leer `telegram_adapter.py` de thea-ia y reescribirlo sabiendo lo que haces produce código mucho mejor que copiar-pegar.

3. **thea-ia es historia personal** — representa meses de aprendizaje y no debe alterarse. Es el punto de partida, no el destino.

4. **thdora tiene arquitectura ABC desde el día 1** — interfaces abstractas, capas bien separadas, documentación por diseño. Mezclar con el código de thea-ia romperia esta coherencia.

---

## La metáfora correcta

> `thea-ia` es la universidad. `thdora` es la carrera profesional.

En la universidad experimentas, fallas, aprendes. En la carrera profesional aplicas todo eso con criterio. No borras los apuntes de la universidad — los consultas cuando los necesitas.

---

## Consecuencias

### Para thea-ia
- ✅ Se mantiene intacto, sin modificaciones
- ✅ No se borra, no se archiva
- ✅ Es referencia histórica y cantera de código
- ✅ Puede evolucionar de forma independiente en el futuro si se desea

### Para thdora
- Cada fase consulta el módulo equivalente de thea-ia antes de implementar
- El código migrado se reescribe limpio, no se copia
- La auditoría `docs/auditoria/thea-ia.md` mapea qué consultar en cada fase

---

## Plan de migración selectiva

| Fase thdora | Módulo thea-ia de referencia | Acción |
|-------------|------------------------------|--------|
| Fase 5 — JsonLifeManager | `models/`, `core/` | Consultar modelos de datos |
| Fase 6 — FastAPI | `api/` | Consultar endpoints |
| Fase 7 — Bot Telegram | `adapters/telegram/bot.py` + `telegram_adapter.py` | Reescribir con criterio |
| Fase 8 — Conversación | `core/conversation_manager.py`, `core/fsm/` | Reescribir con criterio |
| Fase 9 — Ollama IA | `core/orchestrator.py`, `core/nlp_engine.py` | Reescribir con criterio |
| Fase 10+ — BD real | `database/` SQLAlchemy + Alembic | Reescribir con criterio |

---

## Referencias

- [Repo thea-ia](https://github.com/alvarofernandezmota-tech/thea-ia) — proyecto original, intacto
- [Auditoría thea-ia](../../../docs/auditoria/thea-ia.md) — inventario completo de módulos
- [ADR-001](./ADR-001-monorepo.md), [ADR-002](./ADR-002-abc-interfaces.md), [ADR-003](./ADR-003-json-persistence.md)
