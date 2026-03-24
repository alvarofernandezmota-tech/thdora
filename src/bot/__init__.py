"""
Módulo Bot Telegram de THDORA.

Proporciona acceso móvil al ecosistema THDORA mediante Telegram.

Comandos planificados (Fase 7):
    /start          → presentación y ayuda
    /citas          → ver citas del día
    /nueva          → crear nueva cita (ConversationHandler)
    /habito         → registrar hábito
    /resumen        → resumen del día
    /pregunta       → consulta libre a Ollama IA local

Dependencias::

    pip install python-telegram-bot>=21.0

Variables de entorno necesarias::

    TELEGRAM_BOT_TOKEN=<tu_token_de_BotFather>
"""
