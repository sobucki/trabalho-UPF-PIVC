import cv2
import mediapipe as mp
import numpy as np
import os
import time
import urllib.request
from pynput.keyboard import Key, Controller

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')
SVM_PATH = os.path.join(os.path.dirname(__file__), 'gesture_model.xml')
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

GESTURE_NAMES = {
    0: "Mao Aberta (Neutro)",
    1: "Punho Fechado (Sair)",
    2: "Apontar Direita (Avancar)",
}


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


def executar_comando(keyboard, label):
    try:
        if label == 1:
            keyboard.press(Key.esc)
            keyboard.release(Key.esc)
            return "Comando: ESC"
        elif label == 2:
            keyboard.press(Key.right)
            keyboard.release(Key.right)
            return "Comando: SETA DIREITA"
        elif label == 0:
            return "Neutro - sem comando"
    except Exception as e:
        return f"Erro: {e}"
    return "Sem acao"


def main():
    baixar_modelo()

    if not os.path.exists(SVM_PATH):
        print(f"Erro: modelo SVM '{SVM_PATH}' nao encontrado.")
        print("Execute collect_data.py e depois train_classifier.py primeiro.")
        return

    print("Carregando modelo SVM...")
    svm = cv2.ml.SVM_load(SVM_PATH)
    print("Modelo carregado.")

    try:
        keyboard = Controller()
        keyboard_available = True
    except Exception as e:
        print(f"Aviso: teclado indisponivel: {e}")
        keyboard_available = False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: nao foi possivel abrir a webcam.")
        return

    ultimo_gesto = -1
    consecutive_frames = 0
    FRAMES_ESTABILIZACAO = 5
    ultimo_comando_time = 0
    COOLDOWN = 1.2
    ultimo_resultado = "Aguardando gesto..."
    timestamp_ms = 0

    print("\n=== GestureHub POC - Inferencia em Tempo Real ===")
    print("Pressione [q] para sair.\n")

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

            gesto_frame = -1
            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
                desenhar_landmarks(frame, landmarks, w, h)
                features = normalizar_landmarks(landmarks)
                sample = np.array([features], dtype=np.float32)
                _, prediction = svm.predict(sample)
                gesto_frame = int(prediction[0][0])

            # Estabilização temporal
            if gesto_frame != -1:
                if gesto_frame == ultimo_gesto:
                    consecutive_frames += 1
                else:
                    ultimo_gesto = gesto_frame
                    consecutive_frames = 1
            else:
                consecutive_frames = 0
                ultimo_gesto = -1

            # Cooldown e disparo
            if consecutive_frames >= FRAMES_ESTABILIZACAO:
                agora = time.time()
                if agora - ultimo_comando_time > COOLDOWN:
                    if keyboard_available:
                        status = executar_comando(keyboard, ultimo_gesto)
                    else:
                        status = f"[Console] {GESTURE_NAMES[ultimo_gesto]}"
                    ultimo_resultado = f"{GESTURE_NAMES[ultimo_gesto]} -> {status}"
                    ultimo_comando_time = agora
                    consecutive_frames = 0
                    print(f"[EVENTO] {ultimo_resultado}")
                else:
                    ultimo_resultado = f"{GESTURE_NAMES[ultimo_gesto]} (Cooldown)"

            # HUD
            cv2.putText(frame, "GestureHub POC", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            nome_atual = GESTURE_NAMES.get(gesto_frame, "Nenhum")
            cv2.putText(frame, f"Gesto: {nome_atual}", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"Frames estaveis: {consecutive_frames}/{FRAMES_ESTABILIZACAO}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, "Ultima acao:", (10, h - 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(frame, ultimo_resultado, (10, h - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow("GestureHub POC", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("Inferencia finalizada.")


if __name__ == "__main__":
    main()
