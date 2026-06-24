# Reglas del Ecosistema — thdora

> Las reglas completas del ecosistema viven en el documento maestro:
> **[yggdrasil-dew/CONVENCIONES.md](https://github.com/alvarofernandezmota-tech/yggdrasil-dew/blob/main/CONVENCIONES.md)**

Este archivo existe para que cualquier repo del ecosistema tenga la referencia visible sin tener que ir a ygg.

---

## Resumen rápido — lo más importante

1. **Inbox primero.** Toda idea nueva entra por `inbox/` con formato `YYYY-MM-DD-titulo.md`
2. **Commits tipados.** `feat:` `fix:` `docs:` `inbox:` `migrate:` `refactor:` `chore:` `config:`
3. **ADR para decisiones.** Cada decisión importante va en `docs/adr/ADR-NNN-titulo.md`
4. **Sin secrets.** Siempre `.env` + `.gitignore`. El `.env.example` documenta todo.
5. **README responde 6 preguntas.** Qué es, qué no es, qué expone, quién consume, cómo arrancar, estructura.
6. **Leer antes de actuar.** Antes de crear o mover algo: leer CONVENCIONES.md + ECOSISTEMA.md + ESTADO-SISTEMA.md (Regla 15).

---

## Responsabilidad de thdora

- Bots y agentes de chat (Telegram, Discord, etc.)
- Workflows n8n
- Integraciones con servicios externos
- Consume `local-brain:11434` para IA local
- NO gestiona modelos, NO gestiona infra
