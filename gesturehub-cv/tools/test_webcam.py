"""
Script de teste do modelo SVM treinado com HaGRID.
Abre a webcam e exibe o gesto reconhecido em tempo real.

Uso:
    python tools/test_webcam.py
"""
import sys
from pathlib import Path

# Permite importar src/ a partir da raiz do projeto
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2
import mediapipe as mp
import numpy as np

from src.config.paths import HAND_LANDMARKER_MODEL_PATH, GESTURE_SVM_MODEL_PATH
from src.vision.landmark_utils import normalize_landmarks, HAND_CONNECTIONS
from src.vision.gesture_labels import get_gesture_name, GESTURE_LABELS

CONFIDENCE_THRESHOLD = 0.6

GESTURE_NAMES = {info["event"]: info["gesture"] for info in GESTURE_LABELS.values()}


def load_detector():
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(HAND_LANDMARKER_MODEL_PATH)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(options)


def draw_landmarks(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 200, 0), 2)
    for x, y in pts:
        cv2.circle(frame, (x, y), 4, (255, 255, 255), -1)


def main():
    if not HAND_LANDMARKER_MODEL_PATH.exists():
        print(f"Modelo não encontrado: {HAND_LANDMARKER_MODEL_PATH}")
        return
    if not GESTURE_SVM_MODEL_PATH.exists():
        print(f"Modelo SVM não encontrado: {GESTURE_SVM_MODEL_PATH}")
        return

    svm = cv2.ml.SVM_load(str(GESTURE_SVM_MODEL_PATH))
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: não foi possível abrir a webcam.")
        return

    print("Pressione [q] para sair.")
    timestamp_ms = 0

    with load_detector() as detector:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
            result = detector.detect_for_video(mp_image, timestamp_ms)
            timestamp_ms += 33

            gesture_text = "Nenhum gesto"
            color = (100, 100, 100)

            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
                draw_landmarks(frame, landmarks)

                features = normalize_landmarks(landmarks)
                sample = np.array(features, dtype=np.float32).reshape(1, -1)
                _, prediction = svm.predict(sample)
                label = int(prediction[0][0])

                gesture_text = get_gesture_name(label)
                color = (0, 255, 0)

            cv2.putText(frame, "GestureHub - Teste do Modelo", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Gesto: {gesture_text}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            cv2.putText(frame, "[q] Sair", (10, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            cv2.imshow("GestureHub - Teste Webcam", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
