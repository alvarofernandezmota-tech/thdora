# Setup — Entorno local de desarrollo

**Sistema operativo:** Windows 11 + WSL2 (Ubuntu 22.04)  
**Última actualización:** 25 marzo 2026  
**Estado:** ✅ Operativo

> 🔗 **Referencia cruzada:** [`personal/00_sistema/openclaw/README.md`](https://github.com/alvarofernandezmota-tech/personal/blob/main/00_sistema/openclaw/README.md) — documentación completa del ecosistema OpenClaw

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

## 1. Estado del entorno (25 marzo 2026)

| Componente | Versión | Estado | Notas |
|-----------|---------|--------|---------|
| Ubuntu WSL2 | 22.04.5 LTS | ✅ | |
| systemd | activo | ✅ | `/etc/wsl.conf` configurado |
| Node.js | 22.x | ✅ | vía NodeSource |
| OpenClaw | latest | ✅ | Gateway activo `127.0.0.1:18789` |
| GitHub MCP skill | instalado | ⚠️ | Instalado, verificar activo |
| Ollama | 0.18.2 | ✅ | |
| qwen2.5-coder:7b | ~4.7GB | ✅ | Responde correctamente |
| auth-profiles.json | ollama local | ✅ | Creado en `~/.openclaw/agents/main/agent/` |
| CUDA / GPU | GTX 1060 | ⚠️ | **Pendiente activar** — ver sección 4.4 |
| Bot Telegram | emparejado | ✅ | THDORA responde |
| VSCode + OpenClaw ext | instalado | ✅ | |
| Repo thdora | `~/projects/thdora` | ✅ | |

### Errores pendientes

| Error | Estado |
|-------|--------|
| `No API key found for provider "ollama"` aparece en algunos mensajes | ⚠️ Investigar |
| GitHub MCP via Telegram — THDORA no accede a repos todavía | ❌ Pendiente |
| CUDA no activado — Ollama corre en CPU (30-60s respuesta) | ❌ Pendiente |

---

## 2. WSL2 — Configuración base

```bash
# Activar systemd
sudo nano /etc/wsl.conf
```
```ini
[boot]
systemd=true
```
```powershell
# Reiniciar desde PowerShell Windows
wsl --shutdown && wsl
```

---

## 3. OpenClaw — Instalación completa

```bash
# 1. Instalar
curl -fsSL https://openclaw.dev/install.sh | bash
export PATH="$HOME/.openclaw/bin:$PATH"  # añadir a ~/.bashrc

# 2. Setup inicial
openclaw onboard --install-daemon

# 3. Verificar gateway
curl http://127.0.0.1:18789/health

# 4. Instalar GitHub MCP
openclaw skills install github-mcp
export GITHUB_TOKEN="ghp_tu_token"  # añadir a ~/.bashrc

# 5. Configurar Ollama como proveedor
mkdir -p ~/.openclaw/agents/main/agent/
cat > ~/.openclaw/agents/main/agent/auth-profiles.json << 'EOF'
{
  "profiles": [
    {
      "name": "ollama-local",
      "provider": "ollama",
      "baseUrl": "http://localhost:11434",
      "model": "qwen2.5-coder:7b"
    }
  ],
  "default": "ollama-local"
}
EOF

# 6. Reiniciar gateway
openclaw gateway restart

# 7. Emparejar Telegram
openclaw pairing start
openclaw pairing approve
```

---

## 4. Ollama — LLM local

```bash
# Instalar
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull qwen2.5-coder:7b

# Verificar GPU vs CPU
ollama ps  # debe decir 100% GPU (si CUDA activo)
```

### 4.4 Activar CUDA (pendiente)

```bash
# En Windows: instalar driver NVIDIA con soporte WSL2
# En WSL2:
nvidia-smi  # verificar que ve la GPU

# Instalar CUDA Toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update && sudo apt-get install -y cuda-toolkit-12-x

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

---

## 5. Clonar thdora

```bash
cd ~/projects
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora
pip install -e ".[dev]"
pytest tests/  # 57 tests deben pasar
```

---

## 6. Errores conocidos y soluciones

| Error | Solución |
|-------|----------|
| `No API key found for provider "ollama"` | Revisar `auth-profiles.json` + `openclaw gateway restart` |
| `openclaw skills list` se corta | `systemctl restart openclaw-gateway` |
| Ollama responde en 30-60s | CUDA no activo — ver sección 4.4 |
| `GITHUB_TOKEN not found` | `export GITHUB_TOKEN=...` en `~/.bashrc` |

---

_Actualizado: 25 marzo 2026_
