from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from src.config.paths import GESTURE_SVM_MODEL_PATH
from src.vision.landmark_utils import FEATURE_VECTOR_SIZE, normalize_landmarks


class GestureClassifier:
    """
    Loads an OpenCV SVM model and predicts gesture labels from normalized hand landmarks.

    The current SVM model expects 42 features:
    21 hand landmarks x 2 coordinates (x, y).
    """

    def __init__(self, model_path: str | Path) -> None:
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Gesture SVM model not found: {self.model_path}")

        # O OpenCV exige que o caminho seja uma string no carregamento
        self._svm = cv2.ml.SVM_load(str(self.model_path))
        
        if self._svm is None:
            raise RuntimeError(f"Failed to load gesture SVM model: {self.model_path}")

    @property
    def is_loaded(self) -> bool:
        return self._svm is not None

    def _prepare_features(self, features: np.ndarray | list[float]) -> np.ndarray:
        """
        Garante que o vetor de features de entrada possui as condições exatas
        para entrar na memória C do algoritmo OpenCV ML (1 linha, 42 colunas, float32).
        """
        if features is None:
            raise ValueError("features cannot be None.")
            
        features_array = np.array(features, dtype=np.float32)
        
        if features_array.size != FEATURE_VECTOR_SIZE:
            raise ValueError(f"Expected {FEATURE_VECTOR_SIZE} features, got {features_array.size}.")
            
        # Garante shape (1, 42)
        return features_array.reshape(1, FEATURE_VECTOR_SIZE)

    def predict(self, features: np.ndarray | list[float]) -> int:
        """
        Extrai o label previsto a partir do vetor numérico.
        """
        sample = self._prepare_features(features)
        
        # predict retorna uma tupla: (ret_val, resultados)
        _, prediction = self._svm.predict(sample)
        
        # O label inferido fica no index 0 da tupla interna de resultados
        return int(prediction[0][0])

    def predict_from_landmarks(self, landmarks) -> int:
        """
        Helper function que conecta o parser do MediaPipe com o nosso SVM.
        """
        features = normalize_landmarks(landmarks)
        return self.predict(features)


def create_default_gesture_classifier() -> GestureClassifier:
    """
    Instancia o classificador baseado no caminho principal do projeto.
    """
    return GestureClassifier(GESTURE_SVM_MODEL_PATH)
