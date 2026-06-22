from __future__ import annotations

import json
import copy

from src.config.paths import SETTINGS_CONFIG_PATH

DEFAULT_SETTINGS = {
    "cooldown": "1.2s",
    "resolution": "Nativa",
}


def load_settings() -> dict:
    """
    Carrega as configurações gerais salvas pelo usuário.
    Retorna o dicionário de configurações. Em caso de ausência ou
    corrupção, retorna as configurações padrão.
    """
    if not SETTINGS_CONFIG_PATH.exists():
        return copy.deepcopy(DEFAULT_SETTINGS)

    try:
        with open(SETTINGS_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Merge com o default para garantir que novas chaves existam
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings.update(data)
        return settings
    except (json.JSONDecodeError, OSError):
        return copy.deepcopy(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    """Persiste as configurações gerais em disco."""
    SETTINGS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(SETTINGS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
