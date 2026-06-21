from __future__ import annotations

import copy
import json

from src.config.paths import INTEGRATIONS_CONFIG_PATH
from src.integrations.default_configs import DEFAULT_INTEGRATIONS

DEFAULT_ACTIVE_INTEGRATION_ID = "presentations"


def load_integrations() -> tuple[dict, str]:
    """
    Carrega as integrações salvas pelo usuário, se existirem.
    Retorna (integrations, active_integration_id). Em caso de ausência ou
    corrupção do arquivo, retorna a configuração padrão.
    """
    if not INTEGRATIONS_CONFIG_PATH.exists():
        return copy.deepcopy(DEFAULT_INTEGRATIONS), DEFAULT_ACTIVE_INTEGRATION_ID

    try:
        with open(INTEGRATIONS_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        integrations = data["integrations"]
        active_integration_id = data.get("active_integration_id", DEFAULT_ACTIVE_INTEGRATION_ID)

        if active_integration_id not in integrations:
            active_integration_id = next(iter(integrations), DEFAULT_ACTIVE_INTEGRATION_ID)

        return integrations, active_integration_id
    except (json.JSONDecodeError, KeyError, OSError):
        return copy.deepcopy(DEFAULT_INTEGRATIONS), DEFAULT_ACTIVE_INTEGRATION_ID


def save_integrations(integrations: dict, active_integration_id: str) -> None:
    """Persiste as integrações e a integração ativa em disco."""
    INTEGRATIONS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "active_integration_id": active_integration_id,
        "integrations": integrations,
    }

    with open(INTEGRATIONS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
