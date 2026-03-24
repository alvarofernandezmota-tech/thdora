# Setup — Entorno local de desarrollo

**Sistema operativo:** Windows 11 + WSL2 (Ubuntu 22.04)  
**Fecha setup:** 23 marzo 2026  
**Estado:** ✅ Operativo

---

## 0. Hardware de la máquina de desarrollo

| Componente | Especificación | Relevancia para IA |
|-----------|---------------|-------------------|
| **CPU** | Intel i5-8400 (6 núcleos, sin NPU) | Fallback si GPU no disponible |
| **RAM** | 16 GB | Límite para modelos >7B en CPU |
| **GPU** | NVIDIA GTX 1060 — **6 GB VRAM** | ✅ Soporta CUDA (Compute Capability 6.1) |
| **SO** | Windows 11 + WSL2 + Ubuntu 22.04 | CUDA disponible via WSL2 |

### Modelos que caben en la GTX 1060 (6GB VRAM)

| Modelo | VRAM necesaria | Para qué sirve | Estado |
|--------|---------------|----------------|--------|
| `qwen2.5-coder:7b` | ~4.7 GB | ✅ Código, repos, OpenClaw | **Modelo principal** |
| `llama3.2:8b` | ~4.7 GB | General, conversación | Opcional |
| `phi3.5:3.8b` | ~2.3 GB | Tareas rápidas, respuestas cortas | Opcional futuro |
| `qwen2.5:14b` | ~9 GB | ❌ No cabe entero en VRAM | Descartado |

### Rendimiento esperado

| Backend | Primera respuesta | Respuestas siguientes |
|---------|------------------|----------------------|
| **CPU pura** (sin CUDA) | 30–60 segundos | 10–20 segundos |
| **GPU con CUDA** ✅ | 5–15 segundos | 2–5 segundos |

> **⚠️ Problema detectado (24 marzo 2026):** Ollama corre en CPU pura porque CUDA no está activado en WSL2. Ver sección 4.4 para activarlo.

---

## 1. WSL2 — Configuración base

### 1.1 Activar systemd (obligatorio para OpenClaw)

```bash
# Editar configuración WSL
sudo nano /etc/wsl.conf
```

Contenido del archivo:
```ini
[boot]
systemd=true
```

Reiniciar WSL desde PowerShell Windows:
```powershell
wsl --shutdown
wsl
```

Verificar que systemd está activo:
```bash
systemctl --version
# Debe mostrar versión de systemd sin errores
```

---

## 2. Node.js 22 (requerido por OpenClaw)

```bash
# Instalar via NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar
node --version   # v22.x.x
npm --version
```

---

## 3. OpenClaw — Instalación y configuración

### 3.1 Instalar OpenClaw

```bash
# Script oficial de instalación
curl -fsSL https://openclaw.dev/install.sh | bash

# Añadir al PATH (añadir a ~/.bashrc)
export PATH="$HOME/.openclaw/bin:$PATH"
source ~/.bashrc

# Verificar
openclaw --version
```

### 3.2 Iniciar el gateway

```bash
# Iniciar gateway manualmente
openclaw gateway start

# O configurar como servicio systemd (recomendado)
# El gateway corre en: 127.0.0.1:18789
```

Verificar que el gateway está activo:
```bash
curl http://127.0.0.1:18789/health
# Debe responder OK
```

### 3.3 Configurar GitHub MCP skill

```bash
# Instalar skill de GitHub
openclaw skills install github-mcp

# Configurar token de GitHub
# Añadir a ~/.bashrc:
export GITHUB_TOKEN="ghp_tu_token_aqui"
source ~/.bashrc
```

**Cómo obtener el token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Permisos mínimos necesarios: `contents: read/write`, `pull_requests: read/write`, `issues: read/write`
3. Copiar el token y añadirlo al `.bashrc`

### 3.4 Configurar proveedor Ollama (LLM local)

Crear/editar el archivo de autenticación:
```bash
mkdir -p ~/.openclaw/agents/main/agent/
nano ~/.openclaw/agents/main/agent/auth-profiles.json
```

Contenido:
```json
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
```

Reiniciar el gateway tras esta configuración:
```bash
openclaw gateway restart
```

### 3.5 Instalar extensión VSCode

1. Abrir VSCode
2. Extensions (`Ctrl+Shift+X`) → buscar `OpenClaw`
3. Instalar `OpenClaw-VSCode`
4. La extensión se conecta automáticamente al gateway en `127.0.0.1:18789`

---

## 4. Ollama — LLM local

### 4.1 Instalar Ollama

```bash
# Instalación oficial
curl -fsSL https://ollama.ai/install.sh | sh

# Verificar
ollama --version
```

### 4.2 Descargar modelo

```bash
# Modelo principal: qwen2.5-coder:7b (~4.7GB)
ollama pull qwen2.5-coder:7b

# Verificar
ollama list
```

### 4.3 Verificar si usa GPU o CPU

```bash
# Con el modelo cargado (haz una pregunta primero), ejecutar:
ollama ps
```

Output esperado **con GPU**:
```
NAME                    ID              SIZE    PROCESSOR    UNTIL
qwen2.5-coder:7b        ...             5.5 GB  100% GPU     ...
```

Output si está en **CPU pura** (problema):
```
NAME                    ID              SIZE    PROCESSOR    UNTIL
qwen2.5-coder:7b        ...             5.5 GB  100% CPU     ...
```

Si dice `100% CPU` → seguir con sección 4.4.

### 4.4 Activar CUDA en WSL2 (GTX 1060)

**Paso 1 — Instalar drivers NVIDIA en Windows** (no en WSL):
- Descargar desde [nvidia.com/drivers](https://www.nvidia.com/drivers)
- Driver para GTX 1060 con soporte CUDA/WSL2
- Instalar en Windows y reiniciar

**Paso 2 — Verificar que WSL2 ve la GPU:**
```bash
# En WSL2 Ubuntu
nvidia-smi
# Debe mostrar la GTX 1060 con CUDA version
```

**Paso 3 — Instalar CUDA Toolkit en WSL2:**
```bash
# Añadir repositorio NVIDIA CUDA para WSL2
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-x

# Añadir al PATH en ~/.bashrc:
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
source ~/.bashrc
```

**Paso 4 — Verificar que Ollama usa GPU:**
```bash
ollama run qwen2.5-coder:7b
# En otra terminal:
ollama ps
# Debe mostrar: 100% GPU
```

---

## 5. Bot Telegram — Emparejamiento con OpenClaw

### 5.1 Prerequisitos

- Bot de Telegram creado via [@BotFather](https://t.me/BotFather)
- Token del bot guardado en `.env` (nunca en el código)

### 5.2 Emparejar bot con OpenClaw

```bash
# Iniciar proceso de emparejamiento
openclaw pairing start

# Se genera un código de emparejamiento
# Enviar ese código al bot de Telegram
# Luego aprobar desde terminal:
openclaw pairing approve
```

### 5.3 Verificar funcionamiento

1. Abrir Telegram → buscar el bot
2. Enviar cualquier mensaje
3. El bot debe responder usando el LLM local (Ollama)

---

## 6. Clonar y configurar thdora en local

```bash
# Clonar repo
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/alvarofernandezmota-tech/thdora.git
cd thdora

# Opción 1: desde WSL (si code está instalado)
code .

# Opción 2: desde Windows Explorer
# Barra de dirección: \\wsl$\Ubuntu\home\alvaro\projects\thdora
```

### 6.1 Instalar dependencias Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
# Debe pasar los 13 tests de MemoryLifeManager
```

---

## 7. Errores conocidos y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `Wsl/Service/E_UNEXPECTED` | WSL crasheó | `wsl --shutdown` + `wsl` en PowerShell |
| `No API key found for provider "ollama"` | auth-profiles.json mal configurado | Revisar sección 3.4 y reiniciar gateway |
| `openclaw skills list` se corta | Gateway no arrancó con systemd | Verificar `systemctl status` y reiniciar gateway |
| `code: command not found` | VSCode no registrado en WSL | Usar opción `\\wsl$\Ubuntu\...` desde Windows |
| `GITHUB_TOKEN` no encontrado | Variable no exportada | Añadir `export GITHUB_TOKEN=...` al `~/.bashrc` |
| Ollama responde en 30-60s | CUDA no activo, corre en CPU | Seguir sección 4.4 para activar CUDA |

---

## 8. Estado del entorno al 24 marzo 2026

| Componente | Versión | Estado |
|-----------|---------|--------|
| Ubuntu WSL2 | 22.04.5 LTS | ✅ |
| systemd | activo | ✅ |
| Node.js | 22.x | ✅ |
| OpenClaw | latest | ✅ |
| Gateway OpenClaw | 127.0.0.1:18789 | ✅ |
| GitHub MCP skill | instalado | ✅ |
| Ollama | 0.18.2 | ✅ |
| Modelo qwen2.5-coder:7b | ~4.7GB | ✅ |
| CUDA / GPU | GTX 1060 6GB | ⚠️ Pendiente activar |
| Bot Telegram | emparejado | ✅ |
| VSCode + extensión WSL | instalado | ✅ |
| Repo thdora clonado | ~/projects/thdora | ✅ |

---

## 9. Hoja de ruta del hardware

| Horizonte | Acción | Motivo |
|-----------|--------|--------|
| **Ahora** | Activar CUDA en GTX 1060 | x6 velocidad sin coste |
| **Corto plazo** | Opcional: añadir `phi3.5:3.8b` | Respuestas rápidas para tareas simples |
| **Futuro (~500€)** | Mini PC dedicado con GPU dedicada | IA corriendo 24/7 sin ocupar el PC principal |

---

_Creado: 24 marzo 2026 — actualizado con contexto hardware y CUDA_
