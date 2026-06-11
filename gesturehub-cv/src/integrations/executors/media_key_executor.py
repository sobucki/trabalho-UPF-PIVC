from __future__ import annotations

try:
    from pynput.keyboard import Controller, Key
except ImportError:
    Key = None
    Controller = None

from src.integrations.command_executor import CommandExecutionResult

MEDIA_KEY_COMMANDS = {
    "PLAY_PAUSE": getattr(Key, "media_play_pause", None) if Key else None,
    "NEXT_TRACK": getattr(Key, "media_next", None) if Key else None,
    "PREVIOUS_TRACK": getattr(Key, "media_previous", None) if Key else None,
    "VOLUME_UP": getattr(Key, "media_volume_up", None) if Key else None,
    "VOLUME_DOWN": getattr(Key, "media_volume_down", None) if Key else None,
    "MUTE": getattr(Key, "media_volume_mute", None) if Key else None,
}

class MediaKeyExecutor:
    def __init__(self) -> None:
        self._keyboard = None
        self._initialization_error = None

        try:
            if Controller:
                self._keyboard = Controller()
            else:
                self._initialization_error = "Módulo pynput não instalado corretamente."
        except Exception as exc:
            self._initialization_error = str(exc)

    def execute(self, command: str) -> CommandExecutionResult:
        if self._keyboard is None:
            return {
                "executed": False,
                "command_type": "media_key",
                "command": command,
                "message": "Teclado indisponível.",
                "error": self._initialization_error,
            }

        key = MEDIA_KEY_COMMANDS.get(command)

        if key is None:
            return {
                "executed": False,
                "command_type": "media_key",
                "command": command,
                "message": f"Comando de mídia não suportado neste ambiente: {command}",
                "error": None,
            }

        try:
            self._keyboard.press(key)
            self._keyboard.release(key)

            return {
                "executed": True,
                "command_type": "media_key",
                "command": command,
                "message": f"Comando executado: {command}",
                "error": None,
            }
        except Exception as exc:
            return {
                "executed": False,
                "command_type": "media_key",
                "command": command,
                "message": "Erro ao executar comando de mídia.",
                "error": str(exc),
            }
