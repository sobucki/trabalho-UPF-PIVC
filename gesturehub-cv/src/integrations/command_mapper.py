from __future__ import annotations
from typing import TypedDict
import copy

class CommandConfig(TypedDict):
    gesture: str
    event: str
    command_type: str
    command: str
    description: str

class IntegrationConfig(TypedDict):
    name: str
    command_type: str
    commands: list[dict]

class CommandMapper:
    def __init__(
        self,
        integrations: dict,
        active_integration_id: str = "presentations",
    ) -> None:
        self.integrations = copy.deepcopy(integrations)
        self.set_active_integration(active_integration_id)

    @property
    def active_integration_id(self) -> str:
        return self._active_integration_id

    def set_active_integration(self, integration_id: str) -> None:
        if integration_id not in self.integrations:
            raise ValueError(f"Unknown integration id: {integration_id}")
        self._active_integration_id = integration_id

    def get_active_integration(self) -> dict:
        return copy.deepcopy(self.integrations[self._active_integration_id])

    def get_command_for_event(self, event_name: str) -> dict | None:
        integration = self.integrations[self._active_integration_id]
        
        for cmd in integration.get("commands", []):
            if cmd.get("event") == event_name:
                # Retorna dados mistos para facilitar o CommandExecutor
                return {
                    "gesture": cmd.get("gesture"),
                    "event": cmd.get("event"),
                    "command_type": integration.get("command_type", "keyboard"),
                    "command": cmd.get("command"),
                    "description": cmd.get("description"),
                }
                
        return None

    def update_integrations(self, integrations: dict) -> None:
        self.integrations = copy.deepcopy(integrations)
        
        if self._active_integration_id not in self.integrations:
            if "presentations" in self.integrations:
                self._active_integration_id = "presentations"
            elif self.integrations:
                self._active_integration_id = list(self.integrations.keys())[0]

    def list_events_for_active_integration(self) -> list[str]:
        integration = self.integrations[self._active_integration_id]
        return [cmd.get("event") for cmd in integration.get("commands", []) if "event" in cmd]
