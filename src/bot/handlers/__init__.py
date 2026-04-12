"""
Paquete handlers del bot THDORA.
Exporta todo lo necesario para main.py sin cambios en el entrypoint.
"""

# Factories de ConversationHandler
from src.bot.handlers.citas import (
    build_nueva_handler,
    build_edit_apt_handler,
    cmd_citas,
    cb_citas_nav,
    cb_cita_detail,
    cb_apt_delete,
    cb_apt_delete_confirm,
)
from src.bot.handlers.habitos import (
    build_habito_handler,
    build_edit_hab_handler,
    cmd_habitos,
    cb_habitos_nav,
    cb_hab_delete,
    cb_hab_delete_confirm,
    cb_hab_add,
    cb_hab_add_value,
)
from src.bot.handlers.semana import (
    cmd_semana,
    cb_semana_nav,
)
from src.bot.handlers.config import (
    build_config_handler,
)
from src.bot.handlers.menu import (
    cmd_start,
    cb_menu_home,
    cb_quick_dispatch,
)
from src.bot.handlers.common import (
    cmd_cancelar,
    cb_cancel_action,
    cmd_resumen,
    error_handler,
)

__all__ = [
    # Factories
    "build_nueva_handler",
    "build_habito_handler",
    "build_edit_apt_handler",
    "build_edit_hab_handler",
    "build_config_handler",
    # Navegación citas
    "cmd_citas",
    "cb_citas_nav",
    "cb_cita_detail",
    "cb_apt_delete",
    "cb_apt_delete_confirm",
    # Navegación hábitos
    "cmd_habitos",
    "cb_habitos_nav",
    "cb_hab_delete",
    "cb_hab_delete_confirm",
    "cb_hab_add",
    "cb_hab_add_value",
    # Semana
    "cmd_semana",
    "cb_semana_nav",
    # Menú
    "cmd_start",
    "cb_menu_home",
    "cb_quick_dispatch",
    # Comunes
    "cmd_cancelar",
    "cb_cancel_action",
    "cmd_resumen",
    "error_handler",
]
