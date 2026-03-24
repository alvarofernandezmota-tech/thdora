# Setup — Entorno local de desarrollo

**Sistema operativo:** Windows 11 + WSL2 (Ubuntu 22.04)  
**Fecha setup:** 23 marzo 2026  
**Estado:** ✅ Operativo

---

## Prerequisitos Windows

- Windows 11 con WSL2 habilitado
- VSCode instalado en Windows
- Extensión **WSL** de Microsoft instalada en VSCode
- Cuenta GitHub con token fine-grained configurado

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
# Balance óptimo RAM/rendimiento para máquina local
ollama pull qwen2.5-coder:7b

# Verificar
ollama list
# Debe aparecer qwen2.5-coder:7b
```

### 4.3 Test del modelo

```bash
ollama run qwen2.5-coder:7b
# Escribir cualquier mensaje para verificar que responde
# Ctrl+D para salir
```

**Por qué qwen2.5-coder:7b:**
- 7B parámetros: cabe en RAM de máquina de desarrollo sin GPU dedicada
- Especializado en código: mejor para tareas de programación
- ~4.7GB descarga: manejable
- Alternativas descartadas: modelos 13B+ (demasiada RAM), modelos genéricos (peor en código)

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

# Abrir en VSCode
# Opción 1: desde WSL (si code está instalado)
code .

# Opción 2: desde Windows Explorer
# Barra de dirección: \\wsl$\Ubuntu\home\alvaro\projects\thdora
```

### 6.1 Instalar dependencias Python

```bash
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -e ".[dev]"

# Verificar tests
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
| Ollama | latest | ✅ |
| Modelo qwen2.5-coder:7b | ~4.7GB | ✅ |
| Bot Telegram | emparejado | ✅ |
| VSCode + extensión WSL | instalado | ✅ |
| Repo thdora clonado | ~/projects/thdora | ✅ |

---

_Creado: 24 marzo 2026 — basado en el proceso de instalación del 23 marzo 2026_
