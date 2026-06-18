# 🔍 Guía de Depuración de Arranque — THDORA

> Generada el 18 jun 2026 tras resolución de 10 bugs encadenados.
> Sigue este orden SIEMPRE que el bot no arranque.

---

## Secuencia de arranque (orden obligatorio)

```bash
# 1. Ir a la carpeta correcta
cd ~/Projects/thdora
pwd  # debe mostrar /home/varopc/Projects/thdora

# 2. Actualizar código
git pull origin main

# 3. Smoke test (2 min, sin Docker — detecta el 90% de los fallos)
docker compose run --rm bot python scripts/smoke_test.py

# 4. Si smoke pasa → rebuild limpio
docker compose down
docker compose build --no-cache bot
docker compose up -d

# 5. Ver logs en tiempo real
docker compose logs -f bot
```

---

## Si el bot sigue fallando tras el rebuild

### Entrar al contenedor
```bash
docker compose exec bot bash
```

### Checks manuales dentro del contenedor
```bash
# Ver variables de entorno cargadas
env | grep -E 'GROQ|TELEGRAM|GITHUB|AGENT|DB'

# Test de memoria (SqliteSaver + data/)
python -c "
from src.agents.memory.manager import memory_manager
print('checkpointer:', memory_manager.checkpointer)
"

# Test del grafo LangGraph completo
python -c "
from src.agents import build_thdora_graph
graph = build_thdora_graph()
print('Grafo compilado OK')
"

# Test de tools
python -c "
from src.agents.tools.registry import get_all_tools
tools = get_all_tools()
print(f'{len(tools)} tools: {[t.name for t in tools]}')
"

# Test de config
python -c "
from src.config import settings
print('TOKEN ok:', bool(settings.TELEGRAM_BOT_TOKEN))
print('GROQ ok:', bool(settings.GROQ_API_KEY))
print('GITHUB:', repr(settings.GITHUB_TOKEN[:4]) if settings.GITHUB_TOKEN else 'vacio (ok)')
"

# Test ffmpeg
ffmpeg -version | head -1

# Permisos de data/
ls -la /app/data/
```

---

## Tabla de errores → solución rápida

| Error en logs | Causa | Fix |
|---------------|-------|-----|
| `ImportError: cannot import name X` | Imagen desactualizada | `docker compose build --no-cache bot` |
| `ModuleNotFoundError: No module named X` | Paquete no en requirements | Añadir + rebuild |
| `ValidationError` (pydantic) | Variable en `.env` faltante o vacía | Revisar `.env` contra `.env.example` |
| `fatal: not a git repository` | Directorio incorrecto | `cd ~/Projects/thdora` |
| `env file .env not found` | Falta `.env` | `cp ~/dev/thdora/.env .` |
| `attempt to write a readonly database` | Permisos en `data/` | `sudo chown -R 1000:1000 ./data` |
| `OperationalError: unable to open database` | `data/` no existe | `mkdir -p data` o rebuild |
| `ffmpeg: not found` | ffmpeg no instalado | Rebuild imagen (ya incluido desde 18jun) |
| `Connection refused` (API) | API no levantada | `docker compose up -d thdora` primero |

---

## Smoke test — cómo interpretarlo

```
✅ = OK, no hay problema
❌ = FALLO BLOQUEANTE — el bot NO arrancara
⚠️  = WARNING no bloqueante (Groq rate-limit, etc.)
```

Si hay un `❌`, el mensaje te dice exactamente:
- Qué archivo falló
- Qué tipo de error
- La causa exacta

Tráela a Perplexity y se aplica el fix en el repo en menos de 2 minutos.

---

## Estado de fixes aplicados (18 jun 2026)

| # | Archivo | Fix | Commit |
|---|---------|-----|--------|
| 1 | `requirements.txt` | `langgraph-checkpoint-sqlite>=2.0.0` | `bdf82f0` |
| 2 | `pyproject.toml` | deps LangGraph completas | `bdf82f0` |
| 3 | `manager.py` | `os.makedirs("data")` antes de `SqliteSaver` | `6f2caaf` |
| 4 | `main.py` | `_check_api()` retry no-bloqueante | `6f2caaf` |
| 5 | `config.py` | `GITHUB_TOKEN` opcional | `a47965e` |
| 6 | `node.py` | `_tools` lazy con `_tools_cache` + `try/except` | `2896bcf` |
| 7 | `Dockerfile` | `ffmpeg` + `curl` en builder y runtime | `2896bcf` |
| 8 | `smoke_test.py` | 22 checks, Groq `warn_only`, test ffmpeg y tools | `2896bcf` |
