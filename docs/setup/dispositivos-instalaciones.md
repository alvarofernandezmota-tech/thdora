# Laboratorio de Rescate y Recuperación Android

> Documentado: 15 junio 2026  
> Máquina host: varopc (Arch Linux + Hyprland)

---

## 🎯 El Objetivo

Crear un entorno híbrido **(Nativo Arch Linux + Virtualización Windows)** para la recuperación, diagnóstico y desbloqueo (FRP) de dispositivos móviles con procesadores **Unisoc** (Redmi A5) y **Samsung** (Exynos/Snapdragon).

---

## 🖥️ Dispositivos del ecosistema

| Dispositivo | Chip | Rol | Estado |
|-------------|------|-----|--------|
| **varopc** | x86 | PC principal de desarrollo (Arch Linux) | ✅ activo |
| **Samsung (Madre)** | Exynos/Snapdragon | Servidor donde corre THDORA en producción | ✅ activo |
| **Redmi A5** | Unisoc T7250 | Dispositivo objetivo — rescate/FRP | 🔄 en proceso |

---

## ✅ Estado de la Infraestructura

### Host (Arch Linux)
- [x] Entorno: Hyprland + Terminal
- [x] Herramienta nativa: `sfd_tool` compilada y funcional
- [x] Permisos USB: acceso a `/dev/ttyUSB0` y `ttyACM0` (grupos `uucp`, `lock`)
- [x] Control gráfico: `xhost` configurado para evitar bloqueos con `sudo`

### Virtualización (en progreso)
- [x] Dependencias instaladas: `qemu-full`, `virt-manager`, `libvirt`
- [ ] Crear VM Windows (Windows 10 Tiny o 11) para software propietario de reparación
- [ ] Configurar USB passthrough para captura automática del móvil en modo descarga

### Gestión de dispositivos
- [x] Redmi A5 identificado: chip Unisoc T7250, modelo 25028RN03
- [x] Firmware descargado: paquete Fastboot `.tgz` (~4.54 GB)
- [ ] Handshake: inyección de archivos FDL1/FDL2 extraídos para desbloquear protocolo BROM

---

## 📦 Stack instalado en varopc (15/06/2026)

### QEMU + libvirt + virt-manager (139 paquetes)

```bash
sudo pacman -S qemu-full libvirt virt-manager virt-install virt-viewer dnsmasq
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt $USER
```

**Grupos/usuarios creados automáticamente:**
- `libvirt` GID 960 | `qemu` UID/GID 953 | `dnsmasq` UID/GID 957 | `libvirt-qemu` UID/GID 955

---

## 📱 Redmi A5 — ROM y flasheo

### ROM descargada
- **Versión:** `A15.0.26.0.VGWMIXM` (Android 15, MIUI Global)
- **Build:** 27 abril 2026 | **Tamaño:** ~4.54 GB
- **Ruta:** `~/isos/redmi-a5/serenity_global.tgz`

```bash
mkdir -p ~/isos/redmi-a5 && cd ~/isos/redmi-a5
curl -L -C - -o serenity_global.tgz \
  "https://bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com/A15.0.26.0.VGWMIXM/serenity_global-images-A15.0.26.0.VGWMIXM-user-20260427.0000.00-15.0-global-26c6dc7975.tgz"
```

> ⚠️ `wget` no está en varopc — usar siempre `curl -L -C -` para reanudar descargas.

### Estado flasheo
- [ ] ROM descargada completamente
- [ ] Verificar integridad del `.tgz`
- [ ] Extraer FDL1/FDL2 del paquete
- [ ] Flashear en modo BROM con sfd_tool

---

## 🔧 Herramientas de flasheo

### sfd_tool
- **Directorio:** `~/sfd_tool` | **Rama:** `master`
- Para interactuar con el bootloader Unisoc (BROM) del Redmi A5

```bash
# Probado — salió Exit 1 (dispositivo no estaba en modo BROM correcto)
mtk printgpt > mtk_resultado.log 2>&1
```

**Siguiente intento:** asegurarse de estar en modo BROM (Apagado total + Vol↓ + USB).

---

## 🔄 Pipeline de trabajo validado

```
1. CONEXIÓN EN FRÍO
   Apagado total + Vol. Abajo + USB → Modo BROM

2. IDENTIFICACIÓN
   sfd_tool (o herramienta oficial en VM) → leer chip_uid

3. SEGURIDAD  ← OBLIGATORIO antes de tocar nada
   Dump particiones críticas: frp, persist, nvram

4. ACCIÓN
   Eliminar bloqueo FRP o reparar sistema

5. VERIFICACIÓN
   Reboot + validar integridad AVB
```

---

## 💻 VM Windows — Pendiente configurar

### Crear VM
```bash
# Desde virt-manager (GUI) o virsh
# Windows 10 Tiny / 11 — sin software pesado
# RAM: 4GB mínimo | Disco: 60GB
```

### USB Passthrough (clave para capturar el móvil en modo descarga)
```bash
# 1. Conectar móvil en modo descarga
# 2. Identificar el dispositivo
lsusb
# Ejemplo: Bus 001 Device 005: ID 1782:4d00 Spreadtrum...

# 3. En virt-manager → Hardware → Add Hardware → USB Host Device
# Seleccionar el ID del móvil → Apply
# A partir de ahí se captura automáticamente al conectar
```

---

## 🔄 Samsung (Madre) — Reinstalación

> Pendiente — más complejo por firmas Samsung Knox.

- [ ] Backup completo de datos THDORA antes de empezar
- [ ] Documentar modelo exacto y versión firmware actual
- [ ] Proceso de reinstalación
- [ ] Re-deploy de THDORA tras reinstalación (ver `madre-deploy.md`)

---

## ⏭️ Próximos pasos inmediatos

1. Esperar que acabe la descarga ROM Redmi A5
2. Verificar `.tgz` e instalar VM Windows
3. Configurar USB passthrough en virt-manager
4. Intentar handshake BROM con FDL1/FDL2 extraídos
5. Documentar Samsung (Madre) reinstalación
