DEFAULT_INTEGRATIONS = {
    "presentations": {
        "name": "Apresentações",
        "command_type": "keyboard",
        "commands": [
            {
                "gesture": "Mão aberta",
                "event": "GESTURE_PALM",
                "command": "F5",
                "description": "Iniciar apresentação"
            },
            {
                "gesture": "Punho fechado",
                "event": "GESTURE_FIST",
                "command": "Esc",
                "description": "Sair da apresentação"
            },
            {
                "gesture": "Arrastar para direita",
                "event": "GESTURE_SWIPE_RIGHT",
                "command": "Right Arrow",
                "description": "Próximo slide"
            },
            {
                "gesture": "Arrastar para esquerda",
                "event": "GESTURE_SWIPE_LEFT",
                "command": "Left Arrow",
                "description": "Slide anterior"
            },
            {
                "gesture": "Joinha",
                "event": "GESTURE_LIKE",
                "command": "Page Down",
                "description": "Avançar"
            },
            {
                "gesture": "Joinha para baixo",
                "event": "GESTURE_DISLIKE",
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
                "event": "GESTURE_PALM",
                "command": "PLAY_PAUSE",
                "description": "Tocar / Pausar"
            },
            {
                "gesture": "Mudo",
                "event": "GESTURE_MUTE",
                "command": "MUTE",
                "description": "Mutar volume"
            },
            {
                "gesture": "Arrastar para direita",
                "event": "GESTURE_SWIPE_RIGHT",
                "command": "NEXT_TRACK",
                "description": "Próxima faixa"
            },
            {
                "gesture": "Arrastar para esquerda",
                "event": "GESTURE_SWIPE_LEFT",
                "command": "PREVIOUS_TRACK",
                "description": "Faixa anterior"
            },
            {
                "gesture": "Joinha",
                "event": "GESTURE_LIKE",
                "command": "VOLUME_UP",
                "description": "Aumentar volume"
            },
            {
                "gesture": "Joinha para baixo",
                "event": "GESTURE_DISLIKE",
                "command": "VOLUME_DOWN",
                "description": "Diminuir volume"
            }
        ]
    }
}

