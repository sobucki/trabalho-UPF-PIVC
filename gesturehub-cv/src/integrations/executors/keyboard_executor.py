from __future__ import annotations

try:
    from pynput.keyboard import Controller, Key
except ImportError:
    Key = None
    Controller = None

from src.integrations.command_executor import CommandExecutionResult

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

class KeyboardExecutor:
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
                "command_type": "keyboard",
                "command": command,
                "message": "Teclado indisponível.",
                "error": self._initialization_error,
            }

        key = KEYBOARD_COMMANDS.get(command)

        if key is None:
            return {
                "executed": False,
                "command_type": "keyboard",
                "command": command,
                "message": f"Comando de teclado não suportado: {command}",
                "error": None,
            }

        try:
            self._keyboard.press(key)
            self._keyboard.release(key)

            return {
                "executed": True,
                "command_type": "keyboard",
                "command": command,
                "message": f"Comando executado: {command}",
                "error": None,
            }
        except Exception as exc:
            return {
                "executed": False,
                "command_type": "keyboard",
                "command": command,
                "message": "Erro ao executar comando de teclado.",
                "error": str(exc),
            }
