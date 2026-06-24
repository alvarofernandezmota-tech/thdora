# AUDITORÍA MAÑANA — thdora

**Fecha:** 2026-06-24  
**Prioridad:** ALTA

---

## Qué es thdora

Fábrica de bots y agentes. Aquí viven todos los agentes del ecosistema: bots de chat, agentes de terminal, handlers de respuesta. Consume `local-brain` para razonamiento y memoria.

**NO es:** servidor, infraestructura, modelos de IA.

---

## Estructura objetivo

```
thdora/
├── inbox/              ← entradas sin procesar
├── docs/
│   └── adr/            ← decisiones de arquitectura
├── bots/               ← bots de chat (Telegram, web...)
├── agents/             ← agentes de terminal y CLI
├── handlers/           ← lógica de respuesta y routing
├── docker/             ← docker-compose de thdora
├── scripts/            ← scripts de utilidad
└── README.md           ← qué es y cómo funciona
```

---

## TODOs urgentes

- [ ] Limpiar root: borrar archivos basura (`=`, `[bot`, `[thdora]`, `CACHED` y similares)
- [ ] Crear estructura de carpetas si no existe
- [ ] Documentar en README qué es thdora y cómo arrancarlo
- [ ] Conectar con `local-brain` cuando esté creado
- [ ] Decidir primer bot a implementar

---

## Conexión con el ecosistema

```
local-brain:11434  ←  thdora consume Ollama
local-brain:5432   ←  thdora consume pgvector (memoria)
yggdrasil-dew      ←  orquesta el deploy de thdora
```

---

## Reglas de la repo (igual que ygg)

- Una responsabilidad única: bots y agentes
- Todo documentado en `docs/`
- Decisiones de arquitectura en `docs/adr/`
- Inbox para ideas sin procesar
- README siempre actualizado
