import qtawesome as qta
from PySide6.QtGui import QIcon

from .styles import (
    PRIMARY,
    PRIMARY_DARK,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    SUCCESS,
    DANGER,
    WARNING,
    INFO,
    NEUTRAL,
)

WHITE = "#FFFFFF"

def app_icon(name: str, color: str = TEXT_PRIMARY) -> QIcon:
    return qta.icon(name, color=color)

def icon_app_logo() -> QIcon:
    return app_icon("fa6s.hand", WHITE)

def icon_integration() -> QIcon:
    return app_icon("fa6s.plug", TEXT_SECONDARY)

def icon_status(status: str = "PARADO") -> QIcon:
    status_upper = status.upper()
    if status_upper in ["ATIVO", "COMANDO EXECUTADO", "SUCESSO"]:
        return app_icon("fa6s.circle-check", SUCCESS)
    if status_upper in ["ERRO DE CÂMERA", "SEM MÃO DETECTADA", "ERRO"]:
        return app_icon("fa6s.triangle-exclamation", DANGER)
    if status_upper in ["AGUARDANDO", "AGUARDANDO GESTO..."]:
        return app_icon("fa6s.circle-notch", WARNING)
    if status_upper in ["COOLDOWN"]:
        return app_icon("fa6s.clock", INFO)
    return app_icon("fa6s.circle-pause", NEUTRAL)

def icon_processing() -> QIcon:
    return app_icon("fa6s.camera", PRIMARY)

def icon_view_mode() -> QIcon:
    return app_icon("fa6s.eye", TEXT_SECONDARY)

def icon_gesture() -> QIcon:
    return app_icon("fa6s.hand", PRIMARY)

def icon_event() -> QIcon:
    return app_icon("fa6s.calendar-days", TEXT_SECONDARY)

def icon_command() -> QIcon:
    return app_icon("fa6s.terminal", TEXT_SECONDARY)

def icon_confidence() -> QIcon:
    return app_icon("fa6s.chart-simple", TEXT_SECONDARY)

def icon_recognition_status() -> QIcon:
    return app_icon("fa6s.shield-halved", PRIMARY)

def icon_cooldown() -> QIcon:
    return app_icon("fa6s.clock", TEXT_SECONDARY)

def icon_play() -> QIcon:
    return app_icon("fa6s.play", WHITE)

def icon_stop() -> QIcon:
    return app_icon("fa6s.stop", DANGER)

def icon_simulate() -> QIcon:
    return app_icon("fa6s.wand-magic-sparkles", TEXT_PRIMARY)

def icon_settings() -> QIcon:
    return app_icon("fa6s.gear", TEXT_PRIMARY)

def icon_image() -> QIcon:
    return app_icon("fa6s.image", TEXT_PRIMARY)

def icon_video() -> QIcon:
    return app_icon("fa6s.video", TEXT_PRIMARY)
