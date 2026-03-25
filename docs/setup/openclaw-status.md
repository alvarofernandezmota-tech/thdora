# OpenClaw — Estado y arquitectura del ecosistema

> Última actualización: 25 marzo 2026  
> 🔗 **Referencia cruzada:** [`personal/00_sistema/openclaw/README.md`](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/openclaw/README.md)

---

## Qué es OpenClaw en este ecosistema

OpenClaw es el **cerebro del sistema THDORA**. Actualmente corre en local (WSL2) como gateway que conecta:
- El bot de Telegram (interfaz de usuario)
- Ollama/qwen2.5-coder:7b (LLM local)
- GitHub MCP skill (acceso a repos)
- thdora API (gestión de citas y hábitos)

## Arquitectura objetivo

```
TÚ (Telegram)
     │
     ▼
Bot Telegram  ←── src/bot/ (Fase 7)
     │
     ▼
OpenClaw Gateway (127.0.0.1:18789)
     │
     ├── Ollama qwen2.5-coder:7b  ← LLM local (GTX 1060)
     ├── GitHub MCP skill          ← acceso repos
     └── thdora API (FastAPI)       ← citas, hábitos, resumen
```

## Estado de cada conexión

| Conexión | Estado | Pendiente |
|----------|--------|-----------|
| Telegram → OpenClaw | ✅ Emparejado | — |
| OpenClaw → Ollama | ⚠️ Configurado | Resolver error `No API key` |
| OpenClaw → GitHub MCP | ⚠️ Instalado | Verificar activo via Telegram |
| OpenClaw → thdora API | ❌ No conectado | Fase 7 — pendiente |
| Ollama → GPU (CUDA) | ❌ CPU pura | Activar CUDA (ver entorno-local.md §4.4) |

## Comandos útiles de mantenimiento

```bash
# Estado del gateway
openclaw gateway status

# Reiniciar gateway
openclaw gateway restart

# Ver logs en tiempo real
openclaw logs --follow

# Listar skills activos
openclaw skills list

# Verificar Ollama
ollama ps
ollama run qwen2.5-coder:7b
```

## Próximos pasos

1. Resolver error `No API key for provider ollama` definitivamente
2. Verificar GitHub MCP activo desde Telegram
3. Activar CUDA — x6 velocidad de respuesta
4. Conectar thdora API como herramienta de OpenClaw (Fase 7/8)

---

_Ver también: [entorno-local.md](./entorno-local.md) · [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)_
