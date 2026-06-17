from __future__ import annotations
from typing import TypedDict

class CommandExecutionResult(TypedDict):
    executed: bool
    command_type: str
    command: str
    message: str
    error: str | None

from src.integrations.executors.keyboard_executor import KeyboardExecutor
from src.integrations.executors.media_key_executor import MediaKeyExecutor

class CommandExecutor:
    def __init__(self) -> None:
        self._keyboard_executor = KeyboardExecutor()
        self._media_key_executor = MediaKeyExecutor()

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
            return self._keyboard_executor.execute(command_str)
        elif command_type == "media_key":
            return self._media_key_executor.execute(command_str)
        else:
            return {
                "executed": False,
                "command_type": command_type or "-",
                "command": command_str,
                "message": f"Tipo de comando não suportado: {command_type}",
                "error": None,
            }
