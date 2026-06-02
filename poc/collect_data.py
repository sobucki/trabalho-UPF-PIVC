import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import urllib.request

CSV_PATH = os.path.join(os.path.dirname(__file__), 'gesture_data.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

num_landmarks = 21


def baixar_modelo():
    if not os.path.exists(MODEL_PATH):
        print("Baixando modelo hand_landmarker.task...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Modelo baixado.")


def criar_detector():
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(options)


def desenhar_landmarks(frame, landmarks, w, h):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 200, 0), 2)
    for x, y in pts:
        cv2.circle(frame, (x, y), 4, (255, 255, 255), -1)


def normalizar_landmarks(landmarks):
    coords = np.array([[lm.x, lm.y] for lm in landmarks])
    punho = coords[0]
    coords -= punho
    max_dist = np.max(np.linalg.norm(coords, axis=1)) or 1.0
    return (coords / max_dist).flatten()


def salvar_amostra(label, features):
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            header = [f'f{i}' for i in range(2 * num_landmarks)] + ['label']
            writer.writerow(header)
        writer.writerow(list(features) + [label])


def main():
    baixar_modelo()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a webcam.")
        return

    print("\n=== Coletor de Dados de Gestos ===")
    print(" [0] Mão Aberta  [1] Punho Fechado  [2] Apontar Direita  [q] Sair\n")

    contadores = {0: 0, 1: 0, 2: 0}
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row:
                        lbl = int(row[-1])
                        if lbl in contadores:
                            contadores[lbl] += 1
        except Exception:
            pass

    ultimo_salvo = ""
    timestamp_ms = 0

    with criar_detector() as detector:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect_for_video(mp_image, timestamp_ms)
            timestamp_ms += 33

            vetor = None
            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
                desenhar_landmarks(frame, landmarks, w, h)
                vetor = normalizar_landmarks(landmarks)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key in [ord('0'), ord('1'), ord('2')]:
                label = int(chr(key))
                if vetor is not None:
                    salvar_amostra(label, vetor)
                    contadores[label] += 1
                    ultimo_salvo = f"Salvo: classe {label} (Total: {contadores[label]})"
                else:
                    ultimo_salvo = "Erro: Nenhuma mao detectada!"

            cv2.putText(frame, "GestureHub POC - Coleta de Dados", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"[0] Mao Aberta: {contadores[0]}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"[1] Punho Fechado: {contadores[1]}", (10, 95),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"[2] Apontar Direita: {contadores[2]}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            if ultimo_salvo:
                color = (0, 0, 255) if "Erro" in ultimo_salvo else (0, 255, 255)
                cv2.putText(frame, ultimo_salvo, (10, h - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            cv2.imshow("Coletor de Dados de Gestos", frame)

    cap.release()
    cv2.destroyAllWindows()
    print("Coleta finalizada. Arquivo salvo em:", CSV_PATH)


if __name__ == "__main__":
    main()
