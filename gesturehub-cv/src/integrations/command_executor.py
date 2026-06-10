from __future__ import annotations
from typing import TypedDict

try:
    from pynput.keyboard import Key, Controller
except ImportError:
    Key = None
    Controller = None

class CommandExecutionResult(TypedDict):
    executed: bool
    command_type: str
    command: str
    message: str
    error: str | None

KEYBOARD_COMMANDS = {
    "Esc": Key.esc if Key else None,
    "F5": Key.f5 if Key else None,
    "Right Arrow": Key.right if Key else None,
    "Left Arrow": Key.left if Key else None,
    "Page Down": Key.page_down if Key else None,
    "Page Up": Key.page_up if Key else None,
    "Space": Key.space if Key else None,
    "Enter": Key.enter if Key else None,
}

MEDIA_KEY_COMMANDS = {
    "PLAY_PAUSE": getattr(Key, "media_play_pause", None) if Key else None,
    "NEXT_TRACK": getattr(Key, "media_next", None) if Key else None,
    "PREVIOUS_TRACK": getattr(Key, "media_previous", None) if Key else None,
    "VOLUME_UP": getattr(Key, "media_volume_up", None) if Key else None,
    "VOLUME_DOWN": getattr(Key, "media_volume_down", None) if Key else None,
    "MUTE": getattr(Key, "media_volume_mute", None) if Key else None,
}

class CommandExecutor:
    def __init__(self) -> None:
        try:
            if Controller:
                self._keyboard = Controller()
            else:
                self._keyboard = None
        except Exception:
            self._keyboard = None

    def execute(self, command_config: dict | None) -> CommandExecutionResult:
        if command_config is None:
            return {
                "executed": False,
                "command_type": "-",
                "command": "-",
                "message": "Nenhum comando configurado para o evento.",
                "error": None,
            }

        command_type = command_config.get("command_type")
        command_str = command_config.get("command")

        if not command_str:
            return {
                "executed": False,
                "command_type": command_type or "-",
                "command": "-",
                "message": "Ação inválida.",
                "error": "A string do comando está vazia.",
            }

        if command_type == "keyboard":
            return self._execute_keyboard_command(command_str)
        elif command_type == "media_key":
            return self._execute_media_key_command(command_str)
        else:
            return {
                "executed": False,
                "command_type": command_type or "-",
                "command": command_str,
                "message": f"Tipo de comando não suportado: {command_type}",
                "error": None,
            }

    def _execute_keyboard_command(self, command: str) -> CommandExecutionResult:
        if self._keyboard is None:
            return {
                "executed": False,
                "command_type": "keyboard",
                "command": command,
                "message": "Erro de integração com teclado.",
                "error": "Módulo pynput não carregado corretamente.",
            }

        key = KEYBOARD_COMMANDS.get(command)
        if key is None:
            return {
                "executed": False,
                "command_type": "keyboard",
                "command": command,
                "message": "Erro ao executar comando.",
                "error": f"Tecla '{command}' não está mapeada internamente.",
            }

        try:
            self._keyboard.press(key)
            self._keyboard.release(key)
            return {
                "executed": True,
                "command_type": "keyboard",
                "command": command,
                "message": "Comando executado com sucesso.",
                "error": None,
            }
        except Exception as exc:
            return {
                "executed": False,
                "command_type": "keyboard",
                "command": command,
                "message": "Erro ao executar comando.",
                "error": str(exc),
            }

    def _execute_media_key_command(self, command: str) -> CommandExecutionResult:
        if self._keyboard is None:
            return {
                "executed": False,
                "command_type": "media_key",
                "command": command,
                "message": "Erro de integração com teclado.",
                "error": "Módulo pynput não carregado corretamente.",
            }

        key = MEDIA_KEY_COMMANDS.get(command)
        if key is None:
            return {
                "executed": False,
                "command_type": "media_key",
                "command": command,
                "message": "Erro ao executar comando.",
                "error": "Comando de mídia não suportado neste ambiente.",
            }

        try:
            self._keyboard.press(key)
            self._keyboard.release(key)
            return {
                "executed": True,
                "command_type": "media_key",
                "command": command,
                "message": "Comando executado com sucesso.",
                "error": None,
            }
        except Exception as exc:
            return {
                "executed": False,
                "command_type": "media_key",
                "command": command,
                "message": "Erro ao executar comando.",
                "error": str(exc),
            }
