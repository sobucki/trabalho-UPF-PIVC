from __future__ import annotations

from typing import TypedDict


class GestureInfo(TypedDict):
    gesture: str
    event: str
    default_action: str


GESTURE_OPEN_HAND = "GESTURE_OPEN_HAND"
GESTURE_CLOSED_FIST = "GESTURE_CLOSED_FIST"
# GESTURE_POINT_RIGHT represents the static pointing-right gesture recognized by the current SVM model.
# GESTURE_SWIPE_RIGHT should be reserved for a future dynamic swipe gesture.
GESTURE_POINT_RIGHT = "GESTURE_POINT_RIGHT"
NO_GESTURE = "NO_GESTURE"


UNKNOWN_GESTURE: GestureInfo = {
    "gesture": "Nenhum",
    "event": NO_GESTURE,
    "default_action": "Nenhuma ação",
}


GESTURE_LABELS: dict[int, GestureInfo] = {
    0: {
        "gesture": "Mão aberta",
        "event": GESTURE_OPEN_HAND,
        "default_action": "Neutro",
    },
    1: {
        "gesture": "Punho fechado",
        "event": GESTURE_CLOSED_FIST,
        "default_action": "Sair",
    },
    2: {
        "gesture": "Apontar direita",
        "event": GESTURE_POINT_RIGHT,
        "default_action": "Avançar",
    },
}


def get_gesture_info(label: int | None) -> GestureInfo:
    """Retorna o dicionário completo das informações do gesto."""
    if label is None:
        return UNKNOWN_GESTURE.copy()
    return GESTURE_LABELS.get(label, UNKNOWN_GESTURE).copy()


def get_gesture_name(label: int | None) -> str:
    """Retorna apenas o nome amigável do gesto."""
    info = get_gesture_info(label)
    return info["gesture"]


def get_event_name(label: int | None) -> str:
    """Retorna apenas o evento interno associado ao label."""
    info = get_gesture_info(label)
    return info["event"]


def get_default_action(label: int | None) -> str:
    """Retorna apenas a ação padrão textual associada ao label."""
    info = get_gesture_info(label)
    return info["default_action"]


def is_known_label(label: int | None) -> bool:
    """Retorna True se o label existir nos mapeamentos suportados."""
    if label is None:
        return False
    return label in GESTURE_LABELS


def list_supported_gestures() -> list[dict]:
    """Retorna uma lista com todos os gestos suportados e seus metadados."""
    supported = []
    for label, info in GESTURE_LABELS.items():
        item = {"label": label}
        item.update(info)
        supported.append(item)
    return supported
