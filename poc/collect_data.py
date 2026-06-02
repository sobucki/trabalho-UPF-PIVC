import cv2
import mediapipe as mp
import numpy as np
import csv
import os

# Configuração de caminhos e parâmetros
CSV_PATH = os.path.join(os.path.dirname(__file__), 'gesture_data.csv')
num_landmarks = 21

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
    Normaliza os marcos da mão para garantir invariância de translação e escala:
    1. Centraliza todos os marcos subtraindo as coordenadas do punho (Landmark 0).
    2. Redimensiona dividindo pela distância máxima entre o punho e qualquer outro marco.
    3. Retorna um vetor linearizado de 42 características (21 marcos * 2 dimensões: X e Y).
    """
    # Converter para array numpy
    coords = np.array(landmarks)
    
    # 1. Centralização: punho é o marco 0
    punho = coords[0]
    coords_centralizadas = coords - punho
    
    # 2. Redimensionamento: escala com base na maior distância euclidiana do punho
    distancias = np.linalg.norm(coords_centralizadas, axis=1)
    max_dist = np.max(distancias)
    
    if max_dist == 0:
        max_dist = 1.0
        
    coords_normalizadas = coords_centralizadas / max_dist
    
    # 3. Linearização: vetor de 42 posições (x0, y0, x1, y1, ...)
    return coords_normalizadas.flatten()

def salvar_amostra(label, features):
    """Salva a amostra de características e seu rótulo no arquivo CSV."""
    file_exists = os.path.isfile(CSV_PATH)
    
    with open(CSV_PATH, mode='a', newline='') as f:
        writer = csv.writer(f)
        # Escreve o cabeçalho caso o arquivo não exista
        if not file_exists:
            header = [f'x{i}' for i in range(num_landmarks)] + [f'y{i}' for i in range(num_landmarks)]
            # O formato do cabeçalho será x0, y0, x1, y1...
            # Mas como simplificamos no flat, vamos colocar apenas f0...f41
            header = [f'f{i}' for i in range(2 * num_landmarks)] + ['label']
            writer.writerow(header)
            
        # Grava os dados
        row = list(features) + [label]
        writer.writerow(row)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a webcam.")
        return

    print("\n=== Coletor de Dados de Gestos ===")
    print("Mantenha a mão posicionada em frente à câmera e pressione a tecla do rótulo correspondente:")
    print(" Pressione [0] para: Mão Aberta")
    print(" Pressione [1] para: Punho Fechado")
    print(" Pressione [2] para: Apontar Direita / Swipe Direita")
    print(" Pressione [q] para: Sair da aplicação\n")

    contadores = {0: 0, 1: 0, 2: 0}
    
    # Se o arquivo já existir, tenta carregar a contagem inicial
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, 'r') as f:
                reader = csv.reader(f)
                next(reader) # pular cabeçalho
                for row in reader:
                    if row:
                        lbl = int(row[-1])
                        if lbl in contadores:
                            contadores[lbl] += 1
        except Exception:
            pass

    ultimo_salvo = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao capturar frame.")
            break

        # Espelhar horizontalmente para facilitar a visualização do usuário
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Converter BGR (OpenCV) para RGB (MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        vetor_caracteristicas = None

        if result.multi_hand_landmarks:
            # Processa apenas a primeira mão detectada
            hand_landmarks = result.multi_hand_landmarks[0]
            
            # Desenha as conexões e marcos da mão
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Extrair coordenadas 2D relativas
            landmarks_2d = []
            for lm in hand_landmarks.landmark:
                # O MediaPipe fornece coordenadas normalizadas de 0 a 1.
                # Mantemos normalizadas para a normalização de translação e escala
                landmarks_2d.append([lm.x, lm.y])
            
            # Normalizar os marcos
            vetor_caracteristicas = normalizar_landmarks(landmarks_2d)

        # Tratar teclas pressionadas
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key in [ord('0'), ord('1'), ord('2')]:
            label = int(chr(key))
            if vetor_caracteristicas is not None:
                salvar_amostra(label, vetor_caracteristicas)
                contadores[label] += 1
                ultimo_salvo = f"Salvo: {label} (Total: {contadores[label]})"
            else:
                ultimo_salvo = "Erro: Nenhuma mão detectada no frame!"

        # Renderizar informações na tela
        cv2.putText(frame, "GestureHub POC - Coleta de Dados", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, f"[0] Mao Aberta: {contadores[0]} amostras", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"[1] Punho Fechado: {contadores[1]} amostras", (10, 95), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"[2] Apontar Direita: {contadores[2]} amostras", (10, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        if ultimo_salvo:
            color = (0, 0, 255) if "Erro" in ultimo_salvo else (0, 255, 255)
            cv2.putText(frame, ultimo_salvo, (10, h - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Coletor de Dados de Gestos", frame)

    cap.release()
    cv2.destroyAllWindows()
    print("\nColeta finalizada. Arquivo salvo em:", CSV_PATH)

if __name__ == "__main__":
    main()
