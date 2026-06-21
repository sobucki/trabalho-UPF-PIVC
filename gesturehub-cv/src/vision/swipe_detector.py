from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from src.vision.gesture_labels import GESTURE_SWIPE_LEFT, GESTURE_SWIPE_RIGHT

WRIST_LANDMARK_INDEX = 0


@dataclass
class SwipeDetectorConfig:
    """Parâmetros ajustáveis do detector de swipe."""

    # Janela de tempo (segundos) em que o deslocamento é avaliado
    time_window_s: float = 0.7
    # Deslocamento horizontal mínimo, como fração da largura do frame, para disparar o swipe
    min_displacement_ratio: float = 0.22
    # Tempo de cooldown após disparar um swipe, para não disparar repetido no mesmo gesto
    cooldown_s: float = 0.8
    # Tamanho máximo do buffer de posições rastreadas
    max_buffer_size: int = 30


class SwipeDetector:
    """
    Detecta gestos dinâmicos de arrastar (swipe) rastreando a posição
    horizontal do pulso (landmark 0) ao longo do tempo.

    Diferente do classificador SVM (que reconhece poses estáticas),
    este detector precisa de uma sequência de frames para identificar
    o movimento.
    """

    def __init__(self, config: SwipeDetectorConfig | None = None) -> None:
        self.config = config or SwipeDetectorConfig()
        self._positions: deque[tuple[float, float]] = deque(maxlen=self.config.max_buffer_size)
        self._last_swipe_time: float = 0.0

    def reset(self) -> None:
        """Limpa o histórico de posições rastreadas (ex: quando a mão sai de cena)."""
        self._positions.clear()

    def update(self, landmarks, is_palm: bool) -> str | None:
        """
        Atualiza o rastreador com os landmarks do frame atual.

        Args:
            landmarks: sequência de landmarks do MediaPipe (21 pontos),
                com coordenadas x,y normalizadas entre 0 e 1.
            is_palm: True quando o gesto estático atual é a mão aberta (palm).
                O swipe só é rastreado enquanto a mão estiver aberta, para
                evitar que outros movimentos laterais disparem o gesto.

        Returns:
            GESTURE_SWIPE_LEFT, GESTURE_SWIPE_RIGHT ou None se nenhum swipe foi detectado.
        """
        now = time.monotonic()

        if landmarks is None or not is_palm:
            self.reset()
            return None

        wrist = landmarks[WRIST_LANDMARK_INDEX]
        self._positions.append((now, wrist.x))

        # Descarta posições fora da janela de tempo
        cutoff = now - self.config.time_window_s
        while self._positions and self._positions[0][0] < cutoff:
            self._positions.popleft()

        if len(self._positions) < 2:
            return None

        # Em cooldown, não dispara novo swipe
        if now - self._last_swipe_time < self.config.cooldown_s:
            return None

        oldest_x = self._positions[0][1]
        newest_x = self._positions[-1][1]
        displacement = newest_x - oldest_x  # coordenadas normalizadas (0-1)

        if abs(displacement) < self.config.min_displacement_ratio:
            return None

        self._last_swipe_time = now
        self.reset()

        return GESTURE_SWIPE_RIGHT if displacement > 0 else GESTURE_SWIPE_LEFT
