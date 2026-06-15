# Dispositivos e Instalaciones del Ecosistema

> Documentado: 15 junio 2026  
> Máquina: varopc (Arch Linux)

---

## 🖥️ Dispositivos del ecosistema

| Dispositivo | Rol | Estado |
|-------------|-----|--------|
| **varopc** | PC principal de desarrollo (Arch Linux) | ✅ activo |
| **Samsung (Madre)** | Servidor donde corre THDORA en producción | ✅ activo |
| **Redmi A5** | Dispositivo objetivo — se va a reinstalar/flashear | 🔄 en proceso |

---

## 📦 Stack instalado en varopc (15/06/2026)

### QEMU + libvirt + virt-manager
Instalados para gestión de VMs y emulación — necesario para el proceso de flasheo del Redmi A5.

```bash
# Instalación completa (139 paquetes)
sudo pacman -S qemu-full libvirt virt-manager virt-install virt-viewer dnsmasq
```

**Grupos y usuarios creados automáticamente:**
- `libvirt` (GID 960)
- `qemu` (GID 953 / UID 953)
- `dnsmasq` (GID/UID 957)
- `libvirt-qemu` (GID 955 / UID 955)

**Servicios activados:**
```bash
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt $USER
```

---

## 📱 Redmi A5 — Reinstalación

### ROM descargada
- **Versión:** A15.0.26.0.VGWMIXM (Android 15, MIUI Global)
- **Fecha build:** 27 abril 2026
- **Tamaño:** ~4.54 GB
- **Directorio:** `~/isos/redmi-a5/serenity_global.tgz`

```bash
# Descarga (wget no disponible, usar curl)
mkdir -p ~/isos/redmi-a5
cd ~/isos/redmi-a5
curl -L -C - -o serenity_global.tgz \
  "https://bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com/A15.0.26.0.VGWMIXM/serenity_global-images-A15.0.26.0.VGWMIXM-user-20260427.0000.00-15.0-global-26c6dc7975.tgz"
```

> ⚠️ `wget` no está instalado en varopc — usar siempre `curl -L -C -` para reanudar descargas.

### Estado descarga
- [ ] ROM descargada completamente
- [ ] Verificar hash
- [ ] Flashear con sfd_tool / mtkclient

---

## 🔧 Herramientas de flasheo

### sfd_tool
- **Directorio:** `~/sfd_tool`
- **Rama:** `master`
- Usado para interactuar con el bootloader MediaTek (MTK) del Redmi A5

```bash
# Comando probado (salió con Exit 1 — pendiente revisar)
mtk printgpt > mtk_resultado.log 2>&1
```

### Notas MTK
- El `printgpt` falló — revisar si el dispositivo estaba en modo correcto (EDL/BROM)
- Asegurarse de tener los drivers USB correctos antes del siguiente intento

---

## 🔄 Samsung (Madre) — Reinstalación

> Pendiente documentar proceso de reinstalación del servidor Madre.

- [ ] Backup de datos THDORA antes de reinstalar
- [ ] Documentar pasos de reinstalación
- [ ] Re-deploy de THDORA tras reinstalación

---

## ⏭️ Próximos pasos

1. Esperar que termine la descarga de la ROM del Redmi A5
2. Verificar integridad del `.tgz`
3. Flashear con sfd_tool en modo EDL
4. Documentar proceso Samsung (Madre)
