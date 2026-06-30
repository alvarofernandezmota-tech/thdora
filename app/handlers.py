import os
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional

# ==============================================================================
# CONFIGURACIÓN DEL ENTORNO
# ==============================================================================
router = APIRouter()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
VAULT_PATH = Path(os.getenv("VAULT_PATH", "/app/yggdrasil-dew"))

# ==============================================================================
# UTILIDADES
# ==============================================================================
def send_telegram_message(text: str):
    """Envía un mensaje formateado en Markdown a Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Error: Credenciales de Telegram no configuradas.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] Error enviando a Telegram: {e}")

# ==============================================================================
# MODELOS DE DATOS
# ==============================================================================
class DiarioPayload(BaseModel):
    texto: str

class PullPayload(BaseModel):
    modelo: str
    target: str = "ollama"  # 'ollama' o 'ollama-embeddings'

# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("/estado")
def get_estado():
    """Ejecuta docker ps en Madre y envía el resumen a Telegram."""
    try:
        salida = subprocess.check_output(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
            text=True
        )
        msg = f"📊 *Estado de Madre (100.91.112.32)*\n```text\n{salida}\n```"
    except Exception as e:
        msg = f"⚠️ *Error al leer el socket de Docker:* {e}"

    send_telegram_message(msg)
    return {"status": "ok", "accion": "estado_enviado"}


@router.get("/inbox")
def get_inbox():
    """Lista los archivos en el directorio inbox del vault."""
    inbox_dir = VAULT_PATH / "inbox"

    try:
        if not inbox_dir.exists():
            inbox_dir.mkdir(parents=True, exist_ok=True)

        archivos = [f.name for f in inbox_dir.iterdir() if f.is_file()]

        if not archivos:
            msg = "📭 *Inbox vacío.* ¡Todo al día en la Batcueva!"
        else:
            lista_formateada = "\n".join([f"- `{archivo}`" for archivo in archivos])
            msg = f"📥 *Pendientes en Inbox:*\n{lista_formateada}"

    except Exception as e:
        msg = f"⚠️ *Error leyendo el inbox:* {e}"

    send_telegram_message(msg)
    return {"status": "ok", "accion": "inbox_enviado"}


@router.post("/diario")
def save_diario(payload: DiarioPayload):
    """Recibe texto y lo appendea al diario del día en el vault."""
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M")

    diarios_dir = VAULT_PATH / "diarios"
    diarios_dir.mkdir(parents=True, exist_ok=True)

    archivo_diario = diarios_dir / f"{fecha_hoy}-diario.md"

    try:
        with open(archivo_diario, "a", encoding="utf-8") as f:
            f.write(f"## {hora_actual}\n{payload.texto}\n\n")
        msg = f"📝 *Registro guardado:* `{fecha_hoy}-diario.md`"
    except Exception as e:
        msg = f"⚠️ *Error escribiendo en el diario:* {e}"

    send_telegram_message(msg)
    return {"status": "ok", "archivo": archivo_diario.name}


def bg_pull_model(modelo: str, target: str):
    """Tarea en background — descarga modelo vía API HTTP de Ollama."""
    send_telegram_message(f"⏳ *Iniciando descarga:* `{modelo}` en `{target}`...")

    url = f"http://{target}:11434/api/pull"

    try:
        response = requests.post(url, json={"name": modelo, "stream": False}, timeout=3600)

        if response.status_code == 200:
            send_telegram_message(f"✅ *Descarga completada:* `{modelo}` listo en `{target}`.")
        else:
            send_telegram_message(f"❌ *Error al descargar* `{modelo}`: {response.text}")
    except requests.exceptions.RequestException as e:
        send_telegram_message(f"🔌 *Error de red al conectar con* `{target}`: {e}")


@router.post("/pull")
def pull_model(payload: PullPayload, bg_tasks: BackgroundTasks):
    """Recibe orden de descarga y la delega a proceso en segundo plano."""
    bg_tasks.add_task(bg_pull_model, payload.modelo, payload.target)
    return {"status": "ok", "mensaje": "Proceso de descarga iniciado en background"}


@router.post("/webhook/uptime")
async def uptime_webhook(request: Request):
    """Recibe webhooks de Uptime Kuma y genera alertas formateadas en Telegram."""
    try:
        payload = await request.json()

        monitor_name = payload.get("monitor", {}).get("name", "Desconocido")
        heartbeat = payload.get("heartbeat", {})
        status = heartbeat.get("status")  # 1=UP, 0=DOWN, 2=PENDING

        if status == 1:
            icono, estado_str = "✅", "UP"
        elif status == 0:
            icono, estado_str = "🚨", "DOWN"
        else:
            icono, estado_str = "⚠️", "PENDIENTE"

        mensaje_detalle = heartbeat.get("msg", "")
        hora = heartbeat.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        alerta = (
            f"{icono} *Alerta de Monitor: {estado_str}*\n"
            f"*Servicio:* `{monitor_name}`\n"
            f"*Hora:* {hora}\n"
        )
        if mensaje_detalle:
            alerta += f"*Detalle:* {mensaje_detalle}"

        send_telegram_message(alerta)

    except Exception as e:
        print(f"[!] Error procesando webhook de Uptime Kuma: {e}")

    return {"status": "ok"}
