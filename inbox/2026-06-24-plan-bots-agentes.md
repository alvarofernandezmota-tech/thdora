# Plan de Bots y Agentes — thdora

**Fecha:** 2026-06-24

---

## Bots planificados

### Bot Telegram personal
- Conecta con Ollama via local-brain
- Responde preguntas, accede a la memoria vectorial
- Puede ejecutar comandos en el servidor
- Estado: 🔧 Pendiente

### Agente de terminal
- CLI agent que usa Ollama localmente
- Ayuda con comandos, scripts, debugging
- Estado: 🔧 Pendiente

### Bot de control del ecosistema
- Monitoriza servicios docker
- Alerta si algo cae
- Puede reiniciar servicios
- Estado: 🔧 Pendiente

---

## Stack técnico previsto

- **Framework:** Python + LangChain o LlamaIndex
- **Modelos:** via LiteLLM (que apunta a Ollama o APIs externas)
- **Memoria:** pgvector en local-brain
- **Mensajería:** python-telegram-bot
- **Deploy:** Docker en yggdrasil-dew

---

## Primer milestone

Bot Telegram mínimo viable:
1. Recibe mensaje
2. Lo manda a Ollama via local-brain
3. Devuelve respuesta
4. Sin memoria todavía — eso viene después
