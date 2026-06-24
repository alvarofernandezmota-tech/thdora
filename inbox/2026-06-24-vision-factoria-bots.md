---
tags: [vision, factoria, bots, agentes, ollama, ecosistema, thdora, alineacion]
fecha: 2026-06-24
estado: pendiente-procesar
prioridad: alta
ruta: thdora/inbox/2026-06-24-vision-factoria-bots.md
relacionado:
  - "[[thdora/ARCHITECTURE]]"
  - "[[thdora/ROADMAP]]"
  - "[[yggdrasil-dew/ECOSISTEMA]]"
  - "[[yggdrasil-dew/inbox/2026-06-24-sesion-madrugada]]"
  - "[[personal/inbox/2026-06-24-arquitectura-thdora-bots]]"
---

# Visión Thdora — Factoría de Bots — 2026-06-24

> Planteamientos clave de la sesión madrugada 24 jun. No saltarse nada.

---

## Qué es Thdora realmente

**Thdora no es un bot — es una factoría de bots y agentes.**

- Cada bot/agente que nace es una extensión con especialidad propia
- Proyecto **independiente** con su propia vida, no subordinado al ecosistema batcueva
- Multiplatforma: móvil, web, terminal
- Útil para proyectos propios y para otros clientes — escala fuera del uso personal
- Tendrá skills para interactuar con todo el ecosistema existente

## Relación con el ecosistema batcueva

- El bot del ecosistema doméstico será un **repo separado** — no contamina Thdora
- Nace desde Thdora como factoría pero vive independiente
- Nombre del bot pendiente de decidir
- Conectará con: diario `[[personal]]`, infraestructura `[[yggdrasil-dew]]`, batcueva

## Stack IA disponible cuando esté batcueva levantado

| Componente | Rol en Thdora |
|---|---|
| **Ollama** | Cerebro local de todos los agentes, sin depender de APIs externas |
| **n8n** | Orquestador — conecta agentes entre sí y con el mundo |
| **Qdrant** | Memoria vectorial compartida entre todos los bots |
| **LiteLLM** | Proxy unificado para modelos locales y remotos |
| **batcueva** | Infraestructura donde todo corre |

## Repos del ecosistema que se alinean con Thdora

Todas las repos del ecosistema seguirán la misma estructura y convenciones:

| Repo | Rol |
|------|-----|
| `personal` | Contexto vital — Thdora puede leer diario y estado del usuario |
| `yggdrasil-dew` | Infraestructura — Thdora sabe dónde está todo |
| `thdora` | Factoría — proyecto independiente |
| repos por fase (futuro) | Cada fase Docker tendrá su repo estructurado igual |

## Pendientes para Thdora

- [ ] Decidir nombre del bot del ecosistema doméstico
- [ ] Definir skills prioritarias para el bot batcueva
- [ ] Definir cómo Thdora accede al contexto de `personal` (lectura diario, estado)
- [ ] Alinear `ARCHITECTURE.md` con la visión de factoría
- [ ] Crear estructura `inbox/` y convenciones iguales a `yggdrasil-dew`
- [ ] Auditoría limpieza root — hay ficheros basura: `=`, `[bot`, `[thdora`, `naming`, `resolve`, `unpacking`, `exporting`, `CACHED` — eliminar o mover

## Nota sobre la auditoría del root

Se detectaron ficheros basura en el root de la repo que necesitan limpieza:
```
=           ← eliminar
[bot        ← eliminar
[bot]       ← eliminar
[thdora     ← eliminar
[thdora]    ← eliminar
CACHED      ← revisar/eliminar
exporting   ← revisar/eliminar
naming      ← revisar/eliminar
resolve     ← revisar/eliminar
unpacking   ← revisar/eliminar
```
Ejecutar limpieza en próxima sesión.
