# Setup — Entorno local de desarrollo

**Sistema operativo:** Windows 11 + WSL2 (Ubuntu 22.04)  
**Última actualización:** 27 marzo 2026  
**Estado:** ✅ Operativo

> 🔗 **Referencia cruzada:** [`personal/00_sistema/openclaw/README.md`](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/openclaw/README.md)

---

## 0. Hardware

| Componente | Especificación | Relevancia IA |
|-----------|---------------|---------------|
| **CPU** | Intel i5-8400 (6 núcleos) | Fallback sin GPU |
| **RAM** | 16 GB | Límite modelos >7B en CPU |
| **GPU** | NVIDIA GTX 1060 — **6 GB VRAM** | ✅ CUDA Compute 6.1 |
| **SO** | Windows 11 + WSL2 + Ubuntu 22.04 | CUDA vía WSL2 |

### Modelos compatibles (GTX 1060 6GB)

| Modelo | VRAM | Uso | Estado |
|--------|------|-----|--------|
| `qwen2.5-coder:7b` | ~4.7 GB | Código, OpenClaw | ✅ **Modelo activo** |
| `phi3.5:3.8b` | ~2.3 GB | Respuestas rápidas | Opcional |
| `qwen2.5:14b` | ~9 GB | ❌ No cabe en VRAM | Descartado |

---

## 1. Estado del entorno (27 marzo 2026)

| Componente | Versión | Estado | Notas |
|-----------|---------|--------|---------|
| Ubuntu WSL2 | 22.04.5 LTS | ✅ | |
| Python | 3.10 | ✅ | venv en `~/projects/thdora/.venv` |
| systemd | activo | ✅ | `/etc/wsl.conf` configurado |
| Node.js | 22.x | ✅ | vía NodeSource |
| OpenClaw | latest | ✅ | Gateway activo `127.0.0.1:18789` |
| GitHub MCP skill | instalado | ⚠️ | Instalado, verificar activo |
| Ollama | 0.18.2 | ✅ | |
| qwen2.5-coder:7b | ~4.7GB | ✅ | Responde correctamente |
| auth-profiles.json | ollama local | ✅ | Creado en `~/.openclaw/agents/main/agent/` |
| CUDA / GPU | GTX 1060 | ⚠️ | **Pendiente activar** — ver sección 4.4 |
| Bot Telegram | emparejado | ✅ | THDORA responde — token en `.env` |
| VSCode + OpenClaw ext | instalado | ✅ | |
| Repo thdora | `~/projects/thdora` | ✅ | venv creado 27/03/2026 |

### Errores pendientes

| Error | Estado |
|-------|--------|
| `No API key found for provider "ollama"` | ⚠️ Investigar |
| GitHub MCP via Telegram — THDORA no accede a repos todavía | ❌ Pendiente |
| CUDA no activado — Ollama corre en CPU (30-60s respuesta) | ❌ Pendiente F8 |

---

## 2. WSL2 — Configuración base

```bash
sudo nano /etc/wsl.conf
```
```ini
[boot]
systemd=true
```
```powershell
wsl --shutdown && wsl
```

---

## 3. OpenClaw — Instalación completa

```bash
curl -fsSL https://openclaw.dev/install.sh | bash
export PATH="$HOME/.openclaw/bin:$PATH"
openclaw onboard --install-daemon
curl http://127.0.0.1:18789/health
openclaw skills install github-mcp
export GITHUB_TOKEN="ghp_tu_token"
openclaw pairing start
openclaw pairing approve
```

---

## 4. Ollama — LLM local

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5-coder:7b
ollama ps
```

### 4.4 Activar CUDA (pendiente — F8)

```bash
nvidia-smi
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update && sudo apt-get install -y cuda-toolkit-12-x
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

---

## 5. Setup thdora — entorno Python

> ⚠️ `pip install -e ".[dev]"` falla en Python 3.10 con setuptools antiguo.
> Usar instalación directa:

```bash
cd ~/projects/thdora
git clone https://github.com/alvarofernandezmota-tech/thdora.git  # si no existe
cd thdora
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn pydantic "python-telegram-bot>=21.0" httpx pytest pytest-cov pytest-asyncio
```

### Verificar instalación
```bash
pip show python-telegram-bot  # debe mostrar 22.x
pytest tests/ -v               # 57 tests deben pasar
```

### Arrancar para desarrollo (2 terminales)
```bash
# Terminal 1 — API
source .venv/bin/activate
uvicorn src.api.main:app --reload

# Terminal 2 — Bot
source .venv/bin/activate
python -m src.bot.main
```

---

## 6. Variables de entorno (.env)

```bash
# Crear .env en la raíz del proyecto (NO commitear)
cp .env.example .env
# Editar con el token de BotFather
TELEGRAM_BOT_TOKEN=tu_token_aqui
```

---

## 7. Errores conocidos y soluciones

| Error | Solución |
|-------|----------|
| `No module named 'setuptools.backends'` | Usar `pip install` directo, no `pip install -e` |
| `No API key found for provider "ollama"` | Revisar `auth-profiles.json` + `openclaw gateway restart` |
| Ollama responde en 30-60s | CUDA no activo — ver sección 4.4 |
| `GITHUB_TOKEN not found` | `export GITHUB_TOKEN=...` en `~/.bashrc` |

---

_Actualizado: 27 marzo 2026 — venv creado, Python 3.10, deps instaladas_
