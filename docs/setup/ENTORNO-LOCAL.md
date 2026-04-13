# Entorno local — Thdora

## 📍 Ruta del proyecto

El repo está en la capa de **Linux (WSL Ubuntu 22.04)**, no en Windows.

```
# Desde PowerShell (Windows Explorer)
\\wsl.localhost\Ubuntu-22.04\home\alvaro\projects\thdora

# Desde terminal Ubuntu/WSL
/home/alvaro/projects/thdora
# o equivalente:
~/projects/thdora
```

## 🚀 Abrir en VS Code

**Desde PowerShell:**
```powershell
# Abrir VS Code directamente en la ruta WSL
code \\wsl.localhost\Ubuntu-22.04\home\alvaro\projects\thdora
```

**Desde terminal Ubuntu (WSL):**
```bash
cd ~/projects/thdora
code .
```

## ▶️ Arrancar el proyecto

Abrir **dos terminales** en VS Code (`Ctrl+Shift+5` para dividir):

**Terminal 1 — API:**
```bash
make run-api
```

**Terminal 2 — Bot:**
```bash
make run-bot
```

## ⚠️ Notas

- El repo está en WSL, **no en `C:\Users\alvar\Documents`**
- VS Code puede abrirse muy grande la primera vez — usar `Windows + ↓` para restaurar tamaño
- El `.env` con el token de Telegram está en la raíz del proyecto (no subir a GitHub)

---
_Actualizado: 13 abril 2026 — por Perplexity AI MCP_
