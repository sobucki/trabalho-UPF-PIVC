from __future__ import annotations

from typing import TypedDict


class GestureInfo(TypedDict):
    gesture: str
    event: str
    default_action: str


GESTURE_CALL         = "GESTURE_CALL"
GESTURE_DISLIKE      = "GESTURE_DISLIKE"
GESTURE_FIST         = "GESTURE_FIST"
GESTURE_FOUR         = "GESTURE_FOUR"
GESTURE_LIKE         = "GESTURE_LIKE"
GESTURE_MUTE         = "GESTURE_MUTE"
GESTURE_OK           = "GESTURE_OK"
GESTURE_PALM         = "GESTURE_PALM"
GESTURE_PEACE        = "GESTURE_PEACE"
GESTURE_ROCK         = "GESTURE_ROCK"
GESTURE_THREE        = "GESTURE_THREE"
GESTURE_THREE2       = "GESTURE_THREE2"
GESTURE_SWIPE_LEFT   = "GESTURE_SWIPE_LEFT"
GESTURE_SWIPE_RIGHT  = "GESTURE_SWIPE_RIGHT"
NO_GESTURE           = "NO_GESTURE"


UNKNOWN_GESTURE: GestureInfo = {
    "gesture": "Nenhum",
    "event": NO_GESTURE,
    "default_action": "Nenhuma ação",
}


# Labels treinados com o dataset HaGRID (12 classes)
# Unificações aplicadas:
#   stop + stop_inverted → palm
#   peace_inverted + two_up + two_up_inverted → peace
#   one → removido
GESTURE_LABELS: dict[int, GestureInfo] = {
    0: {
        "gesture": "Telefone",
        "event": GESTURE_CALL,
        "default_action": "Nenhuma ação",
    },
    1: {
        "gesture": "Joinha para baixo",
        "event": GESTURE_DISLIKE,
        "default_action": "Nenhuma ação",
    },
    2: {
        "gesture": "Punho fechado",
        "event": GESTURE_FIST,
        "default_action": "Nenhuma ação",
    },
    3: {
        "gesture": "Quatro dedos",
        "event": GESTURE_FOUR,
        "default_action": "Nenhuma ação",
    },
    4: {
        "gesture": "Joinha",
        "event": GESTURE_LIKE,
        "default_action": "Nenhuma ação",
    },
    5: {
        "gesture": "Mudo",
        "event": GESTURE_MUTE,
        "default_action": "Nenhuma ação",
    },
    6: {
        "gesture": "Ok",
        "event": GESTURE_OK,
        "default_action": "Nenhuma ação",
    },
    7: {
        "gesture": "Mão aberta",
        "event": GESTURE_PALM,
        "default_action": "Nenhuma ação",
    },
    8: {
        "gesture": "Paz",
        "event": GESTURE_PEACE,
        "default_action": "Nenhuma ação",
    },
    9: {
        "gesture": "Rock",
        "event": GESTURE_ROCK,
        "default_action": "Nenhuma ação",
    },
    10: {
        "gesture": "Três dedos",
        "event": GESTURE_THREE,
        "default_action": "Nenhuma ação",
    },
    11: {
        "gesture": "Três dedos (variante)",
        "event": GESTURE_THREE2,
        "default_action": "Nenhuma ação",
    },
}


# Gestos dinâmicos (não vêm do SVM, são emitidos pelo SwipeDetector)
SWIPE_INFO: dict[str, GestureInfo] = {
    GESTURE_SWIPE_LEFT: {
        "gesture": "Arrastar para esquerda",
        "event": GESTURE_SWIPE_LEFT,
        "default_action": "Nenhuma ação",
    },
    GESTURE_SWIPE_RIGHT: {
        "gesture": "Arrastar para direita",
        "event": GESTURE_SWIPE_RIGHT,
        "default_action": "Nenhuma ação",
    },
}


def get_gesture_info(label: int | None) -> GestureInfo:
    if label is None:
        return UNKNOWN_GESTURE.copy()
    return GESTURE_LABELS.get(label, UNKNOWN_GESTURE).copy()


def get_gesture_name(label: int | None) -> str:
    return get_gesture_info(label)["gesture"]


def get_event_name(label: int | None) -> str:
    return get_gesture_info(label)["event"]


def get_default_action(label: int | None) -> str:
    return get_gesture_info(label)["default_action"]


def is_known_label(label: int | None) -> bool:
    if label is None:
        return False
    return label in GESTURE_LABELS


def list_supported_gestures() -> list[dict]:
    supported = []
    for label, info in GESTURE_LABELS.items():
        item = {"label": label}
        item.update(info)
        supported.append(item)
    return supported
