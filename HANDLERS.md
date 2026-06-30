# THDORA Handlers — Fase 6

> Endpoints FastAPI implementados el 30-jun-2026 vía Gemini + Perplexity MCP

## Variables de entorno requeridas

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
VAULT_PATH=/app/yggdrasil-dew
```

## Volúmenes Docker requeridos en thdora

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock  # para /estado
  - /home/varopc/yggdrasil-dew:/app/yggdrasil-dew  # para /inbox y /diario
```

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| GET | `/estado` | `docker ps` → Telegram Markdown |
| GET | `/inbox` | Lista `inbox/` del vault → Telegram |
| POST | `/diario` | Appenda texto a `diarios/YYYY-MM-DD-diario.md` |
| POST | `/pull` | Descarga modelo Ollama en background vía API HTTP |
| POST | `/webhook/uptime` | Recibe Uptime Kuma → alerta Telegram formateada |

## Cómo probar

```bash
# /estado
curl http://100.91.112.32:8000/estado

# /inbox
curl http://100.91.112.32:8000/inbox

# /diario
curl -X POST http://100.91.112.32:8000/diario \
  -H 'Content-Type: application/json' \
  -d '{"texto": "Probando handler diario desde curl"}'

# /pull
curl -X POST http://100.91.112.32:8000/pull \
  -H 'Content-Type: application/json' \
  -d '{"modelo": "llama3.1:8b", "target": "ollama"}'
```

## Arquitectura

```
Telegram Bot
    ↓
thdora-bot (Python)
    ↓ HTTP
thdora (FastAPI :8000)
    ├─ /estado     → docker.sock → Madre
    ├─ /inbox      → vault/inbox/
    ├─ /diario     → vault/diarios/
    ├─ /pull       → ollama API :11434 / :11435
    └─ /webhook    → Uptime Kuma → Telegram
```

---
_Creado: 30 jun 2026 04:50 CEST — Gemini 2.5 Pro + Perplexity MCP_
