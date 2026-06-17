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


def aplicar_clahe(frame):
    # Melhora o contraste da imagem (ajuda o MediaPipe em baixa luminosidade)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)


def destacar_mao(frame, landmarks, w, h):
    # Pega os pontos da mao e cria uma forma convexa envolta deles
    pts = np.array([[int(lm.x * w), int(lm.y * h)] for lm in landmarks], dtype=np.int32)
    hull = cv2.convexHull(pts)
    
    # Cria uma mascara preta do tamanho da imagem
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Preenche o poligono da mao com branco
    cv2.fillConvexPoly(mask, hull, 255)
    
    # Aumenta a area da mascara para cobrir dedos gordinhos (Kernel reduzido de 50 para 25 p/ performance)
    kernel = np.ones((25, 25), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    # Borra a mascara para fazer uma transicao suave (Efeito Esfumaçado mais leve: 31x31)
    mask = cv2.GaussianBlur(mask, (31, 31), 0)
    
    # Fundo escuro em tons de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    bg = cv2.convertScaleAbs(gray, alpha=0.1, beta=0)
    
    # Mistura a imagem original com o fundo, baseado na mascara
    mask_normalized = mask.astype(float) / 255.0
    mask_3d = np.repeat(mask_normalized[:, :, np.newaxis], 3, axis=2)
    resultado = (frame * mask_3d + bg * (1 - mask_3d)).astype(np.uint8)
    
    return resultado


def aplicar_filtros(frame, modo_filtro):
    if modo_filtro == 'normal':
        return frame
        
    resultado = frame.copy()
    
    if modo_filtro == 'gray':
        # Tons de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resultado = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    elif modo_filtro == 'hsv':
        # Conversao para HSV
        resultado = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    elif modo_filtro == 'blur':
        # Suavizacao / Borrao (Gaussian Blur)
        resultado = cv2.GaussianBlur(frame, (15, 15), 0)
    elif modo_filtro == 'thresh':
        # Binarizacao (Thresholding)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        resultado = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    elif modo_filtro == 'edges':
        # Deteccao de bordas (Canny)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        resultado = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
    return resultado


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
    modo_filtro = 'normal'

    print("\n=== GestureHub POC - Inferencia em Tempo Real ===")
    print("Filtros disponiveis:")
    print("  [n] Normal")
    print("  [g] Tons de Cinza (Grayscale)")
    print("  [h] HSV")
    print("  [b] Gaussian Blur")
    print("  [t] Binarizacao (Threshold)")
    print("  [e] Detector de Bordas (Canny)")
    print("  [c] CLAHE (Melhora Iluminacao p/ MediaPipe)")
    print("  [d] Destaque (Isola a mao com Mascara Inteligente)")
    print("Pressione [q] para sair.\n")

    with criar_detector() as detector:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # OTIMIZACAO DE PERFORMANCE:
            # Webcams de Mac filmam em alta definicao (HD/FullHD), o que deixa
            # as operacoes matematicas dos filtros pesadas na CPU.
            # Baixar para 640x480 aumenta o FPS absurdamente sem perder precisao na deteccao!
            # frame = cv2.resize(frame, (640, 480))

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            if modo_filtro == 'clahe':
                # Processamento ANTES do MediaPipe para ajuda-lo fisicamente
                frame = aplicar_clahe(frame)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect_for_video(mp_image, timestamp_ms)
            timestamp_ms += 33

            # Aplica os filtros na imagem de exibicao (exceto Destaque, que precisa dos landmarks)
            if modo_filtro not in ['destaque', 'clahe']:
                frame = aplicar_filtros(frame, modo_filtro)

            gesto_frame = -1
            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
                
                # Se o modo for destaque, usa a inteligencia dos landmarks para isolar a mao
                if modo_filtro == 'destaque':
                    frame = destacar_mao(frame, landmarks, w, h)
                    
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
            
            # Info do Filtro
            cv2.putText(frame, f"Filtro: {modo_filtro.upper()}", (10, h - 85),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                        
            cv2.putText(frame, "Ultima acao:", (10, h - 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(frame, ultimo_resultado, (10, h - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow("GestureHub POC", frame)
            
            # Tratamento de teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'): modo_filtro = 'normal'
            elif key == ord('g'): modo_filtro = 'gray'
            elif key == ord('h'): modo_filtro = 'hsv'
            elif key == ord('b'): modo_filtro = 'blur'
            elif key == ord('t'): modo_filtro = 'thresh'
            elif key == ord('e'): modo_filtro = 'edges'
            elif key == ord('c'): modo_filtro = 'clahe'
            elif key == ord('d'): modo_filtro = 'destaque'

    cap.release()
    cv2.destroyAllWindows()
    print("Inferencia finalizada.")


if __name__ == "__main__":
    main()
