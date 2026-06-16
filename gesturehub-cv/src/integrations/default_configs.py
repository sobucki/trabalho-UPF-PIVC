DEFAULT_INTEGRATIONS = {
    "presentations": {
        "name": "Apresentações",
        "command_type": "keyboard",
        "commands": [
            {
                "gesture": "Mão aberta",
                "event": "GESTURE_OPEN_HAND",
                "command": "F5",
                "description": "Iniciar apresentação"
            },
            {
                "gesture": "Punho fechado",
                "event": "GESTURE_CLOSED_FIST",
                "command": "Esc",
                "description": "Sair da apresentação"
            },
            {
                "gesture": "Swipe direita",
                "event": "GESTURE_SWIPE_RIGHT",
                "command": "Right Arrow",
                "description": "Próximo slide"
            },
            {
                "gesture": "Swipe esquerda",
                "event": "GESTURE_SWIPE_LEFT",
                "command": "Left Arrow",
                "description": "Slide anterior"
            },
            {
                "gesture": "Apontar direita",
                "event": "GESTURE_POINT_RIGHT",
                "command": "Right Arrow",
                "description": "Avançar slide"
            },
            {
                "gesture": "Polegar cima",
                "event": "GESTURE_THUMB_UP",
                "command": "Page Down",
                "description": "Avançar"
            },
            {
                "gesture": "Polegar baixo",
                "event": "GESTURE_THUMB_DOWN",
                "command": "Page Up",
                "description": "Voltar"
            }
        ]
    },
    "media": {
        "name": "Spotify / Mídia",
        "command_type": "media_key",
        "commands": [
            {
                "gesture": "Mão aberta",
                "event": "GESTURE_OPEN_HAND",
                "command": "PLAY_PAUSE",
                "description": "Tocar / Pausar"
            },
            {
                "gesture": "Punho fechado",
                "event": "GESTURE_CLOSED_FIST",
                "command": "MUTE",
                "description": "Mutar volume"
            },
            {
                "gesture": "Swipe direita",
                "event": "GESTURE_SWIPE_RIGHT",
                "command": "NEXT_TRACK",
                "description": "Próxima faixa"
            },
            {
                "gesture": "Swipe esquerda",
                "event": "GESTURE_SWIPE_LEFT",
                "command": "PREVIOUS_TRACK",
                "description": "Faixa anterior"
            },
            {
                "gesture": "Apontar direita",
                "event": "GESTURE_POINT_RIGHT",
                "command": "NEXT_TRACK",
                "description": "Próxima faixa"
            },
            {
                "gesture": "Polegar cima",
                "event": "GESTURE_THUMB_UP",
                "command": "VOLUME_UP",
                "description": "Aumentar volume"
            },
            {
                "gesture": "Polegar baixo",
                "event": "GESTURE_THUMB_DOWN",
                "command": "VOLUME_DOWN",
                "description": "Diminuir volume"
            }
        ]
    }
}
