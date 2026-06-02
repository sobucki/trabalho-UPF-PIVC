import cv2
import mediapipe as mp
import numpy as np
import os
import time
from pynput.keyboard import Key, Controller

# Configurações de caminhos
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'gesture_model.xml')

# Mapeamento de rótulos para nomes de gestos e comandos
GESTURE_NAMES = {
    0: "Mao Aberta (Neutro)",
    1: "Punho Fechado (Sair)",
    2: "Apontar Direita (Avancar)"
}

# Inicializa o controlador do teclado
try:
    keyboard = Controller()
    keyboard_available = True
except Exception as e:
    print(f"Aviso: Não foi possível inicializar o controlador de teclado pynput: {e}")
    keyboard_available = False

# Inicializa o MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

def normalizar_landmarks(landmarks):
    """
    Função de normalização idêntica à do collect_data.py para manter a consistência.
    """
    coords = np.array(landmarks)
    punho = coords[0]
    coords_centralizadas = coords - punho
    distancias = np.linalg.norm(coords_centralizadas, axis=1)
    max_dist = np.max(distancias)
    if max_dist == 0:
        max_dist = 1.0
    coords_normalizadas = coords_centralizadas / max_dist
    return coords_normalizadas.flatten()

def executar_comando(label):
    """Simula a tecla no teclado correspondente ao gesto detectado."""
    if not keyboard_available:
        return f"[Console Only] Tecla simulada para Classe {label}"
        
    try:
        if label == 1: # Punho Fechado -> ESC
            keyboard.press(Key.esc)
            keyboard.release(Key.esc)
            return "Comando Enviado: ESC (Sair)"
        elif label == 2: # Apontar Direita -> Right Arrow
            keyboard.press(Key.right)
            keyboard.release(Key.right)
            return "Comando Enviado: SETA DIREITA (Avancar)"
        elif label == 0: # Mão Aberta -> Sem comando (neutro)
            return "Gesto Neutro detectado - Nenhuma tecla enviada"
    except Exception as e:
        return f"Erro ao enviar comando: {e}"
    return "Nenhuma acao configurada"

def main():
    # 1. Verificar e carregar o modelo SVM
    if not os.path.exists(MODEL_PATH):
        print(f"Erro: O arquivo do modelo '{MODEL_PATH}' nao foi encontrado.")
        print("Por favor, execute o collect_data.py primeiro para capturar dados e depois o train_classifier.py.")
        return

    print("Carregando o modelo SVM da OpenCV...")
    svm = cv2.ml.SVM_load(MODEL_PATH)
    print("Modelo carregado com sucesso!")

    # 2. Inicializar a webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Nao foi possivel abrir a webcam.")
        return

    # Parâmetros de Estabilização e Cooldown
    ultimo_gesto_estavel = -1
    consecutive_frames = 0
    FRAMES_ESTABILIZACAO = 5  # O gesto precisa aparecer por 5 frames consecutivos
    
    ultimo_comando_time = 0
    COOLDOWN_COMMAND = 1.2    # Segundos de intervalo mínimo entre execuções de comandos

    ultimo_resultado_txt = "Aguardando gesto..."

    print("\n=== Infeferencia de Gestos em Tempo Real ===")
    print("Mantenha a mao posicionada em frente a camera.")
    print(" - Faca Punho Fechado para enviar [ESC]")
    print(" - Faca Apontar Direita para enviar [SETA DIREITA]")
    print(" Pressione [q] na janela de video para sair da aplicacao.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao capturar frame.")
            break

        # Espelhar para visualização natural (efeito espelho)
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Converter para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        gesto_detectado_no_frame = -1
        confianca_txt = "N/A"

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extrair e normalizar coordenadas
            landmarks_2d = [[lm.x, lm.y] for lm in hand_landmarks.landmark]
            features = normalizar_landmarks(landmarks_2d)

            # Preparar o vetor para a predição da OpenCV (precisa ser float32 bidimensional 1x42)
            sample = np.array([features], dtype=np.float32)

            # Fazer a predição
            _, prediction = svm.predict(sample)
            gesto_detectado_no_frame = int(prediction[0][0])
            
            # Como o SVM clássico linear retorna apenas a classe mais próxima,
            # a confiança pode ser considerada binária para esta POC linear.
            confianca_txt = "Alta"

        # Lógica de Estabilização Temporal
        if gesto_detectado_no_frame != -1:
            if gesto_detectado_no_frame == ultimo_gesto_estavel:
                consecutive_frames += 1
            else:
                ultimo_gesto_estavel = gesto_detectado_no_frame
                consecutive_frames = 1
        else:
            consecutive_frames = 0
            ultimo_gesto_estavel = -1

        # Lógica de Trigger de Comando com Cooldown
        if consecutive_frames >= FRAMES_ESTABILIZACAO:
            tempo_atual = time.time()
            if tempo_atual - ultimo_comando_time > COOLDOWN_COMMAND:
                # Executa o comando correspondente à classe estabilizada
                status_cmd = executar_comando(ultimo_gesto_estavel)
                ultimo_resultado_txt = f"{GESTURE_NAMES[ultimo_gesto_estavel]} -> {status_cmd}"
                ultimo_comando_time = tempo_atual
                print(f"[EVENTO] {ultimo_resultado_txt}")
                # Resetar contador para evitar disparos repetidos antes do cooldown
                consecutive_frames = 0
            else:
                ultimo_resultado_txt = f"{GESTURE_NAMES[ultimo_gesto_estavel]} (Aguardando Cooldown)"

        # Exibir informações na interface
        cv2.putText(frame, "GestureHub POC - Reconhecimento em Tempo Real", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Gesto detectado no frame atual
        nome_atual = GESTURE_NAMES.get(gesto_detectado_no_frame, "Nenhum")
        cv2.putText(frame, f"Gesto no Frame: {nome_atual}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Estado de estabilização
        cv2.putText(frame, f"Frames Estaveis: {consecutive_frames}/{FRAMES_ESTABILIZACAO}", (10, 95), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Última ação enviada
        cv2.putText(frame, "Ultima Acao:", (10, h - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(frame, ultimo_resultado_txt, (10, h - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Reconhecimento de Gestos POC", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Inferencia finalizada.")

if __name__ == "__main__":
    main()
