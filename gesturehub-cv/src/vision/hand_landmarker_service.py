from __future__ import annotations

import os
from pathlib import Path
from types import TracebackType
from typing import Type

import mediapipe as mp
import numpy as np

from src.config.paths import HAND_LANDMARKER_MODEL_PATH


class HandLandmarkerService:
    """
    Serviço que encapsula a lógica pesada de inicialização, detecção 
    e liberação do modelo MediaPipe HandLandmarker.
    """
    def __init__(
        self,
        model_path: str | Path,
        num_hands: int = 1,
        min_hand_detection_confidence: float = 0.7,
        min_hand_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self.model_path = Path(model_path)
        self.num_hands = num_hands
        self.min_hand_detection_confidence = min_hand_detection_confidence
        self.min_hand_presence_confidence = min_hand_presence_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self._detector = None

    @property
    def is_started(self) -> bool:
        return self._detector is not None

    def start(self) -> None:
        """
        Carrega o modelo .task e inicializa o detector na API vision do MediaPipe.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"MediaPipe hand landmarker model not found: {self.model_path}"
            )

        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        base_options = python.BaseOptions(model_asset_path=str(self.model_path))
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=self.num_hands,
            min_hand_detection_confidence=self.min_hand_detection_confidence,
            min_hand_presence_confidence=self.min_hand_presence_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )

        self._detector = vision.HandLandmarker.create_from_options(options)

    def _validate_rgb_frame(self, rgb_frame: np.ndarray) -> np.ndarray:
        """
        Valida a matriz numpy e garante um frame contíguo.
        """
        if not isinstance(rgb_frame, np.ndarray):
            raise ValueError("rgb_frame must be a numpy.ndarray.")

        if rgb_frame.ndim != 3 or rgb_frame.shape[2] != 3:
            raise ValueError("rgb_frame must be a valid RGB image with shape (height, width, 3).")

        return np.ascontiguousarray(rgb_frame)

    def detect(self, rgb_frame: np.ndarray, timestamp_ms: int):
        """
        Aplica a detecção no frame RGB.
        O frame já deve estar em formato SRGB.
        """
        if not self.is_started:
            raise RuntimeError("HandLandmarkerService must be started before detection.")
            
        validated_frame = self._validate_rgb_frame(rgb_frame)
        
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=validated_frame
        )
        
        return self._detector.detect_for_video(mp_image, timestamp_ms)

    def close(self) -> None:
        """
        Libera o modelo carregado da memória.
        """
        if self._detector is not None:
            self._detector.close()
            self._detector = None

    def __enter__(self) -> "HandLandmarkerService":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


def create_default_hand_landmarker_service() -> HandLandmarkerService:
    """
    Função utilitária que instancia o serviço com o modelo padrão.
    Não executa `start()` automaticamente.
    """
    return HandLandmarkerService(HAND_LANDMARKER_MODEL_PATH)
