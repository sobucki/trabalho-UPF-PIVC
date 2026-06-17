from typing import Any, Sequence
import numpy as np

NUM_HAND_LANDMARKS = 21
LANDMARK_COORDINATES = 2
FEATURE_VECTOR_SIZE = NUM_HAND_LANDMARKS * LANDMARK_COORDINATES

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

def landmarks_to_xy_array(landmarks: Sequence[Any]) -> np.ndarray:
    """
    Converte a sequência de landmarks do MediaPipe para um array NumPy (21, 2).
    Ignora a coordenada z, retornando apenas x e y em float32.
    """
    if not landmarks:
        raise ValueError("Expected 21 hand landmarks, got none.")
        
    if len(landmarks) != NUM_HAND_LANDMARKS:
        raise ValueError(f"Expected 21 hand landmarks, got {len(landmarks)}.")
        
    coords = []
    for lm in landmarks:
        if not hasattr(lm, 'x') or not hasattr(lm, 'y'):
            raise ValueError("Landmark element is missing 'x' or 'y' attribute.")
        coords.append([lm.x, lm.y])
        
    return np.array(coords, dtype=np.float32)

def normalize_xy_coordinates(coords: np.ndarray) -> np.ndarray:
    """
    Normaliza as coordenadas recebendo array de shape (21, 2).
    Subtrai a posição do punho (índice 0) de todas as coordenadas
    e divide pela maior distância encontrada.
    """
    # Usar cópia para não alterar o array original in-place
    coords_normalized = coords.copy()
    
    punho = coords_normalized[0]
    coords_normalized -= punho
    
    max_dist = np.max(np.linalg.norm(coords_normalized, axis=1))
    if max_dist == 0.0:
        max_dist = 1.0
        
    return coords_normalized / max_dist

def flatten_landmarks(coords: np.ndarray) -> np.ndarray:
    """
    Recebe um array de shape (21, 2) e converte num array flat de (42,) em float32.
    """
    return coords.flatten().astype(np.float32)

def normalize_landmarks(landmarks: Sequence[Any]) -> np.ndarray:
    """
    Pipeline completo: 
    Converte landmarks brutos em (21,2), normaliza pelo punho, 
    escala pela maior distância e achata para (42,) floats.
    """
    coords = landmarks_to_xy_array(landmarks)
    normalized_coords = normalize_xy_coordinates(coords)
    return flatten_landmarks(normalized_coords)

# Alias para compatibilidade momentânea
normalizar_landmarks = normalize_landmarks

# --- Teste conceitual opcional ---
# Pode ser rodado no terminal executando apenas `python src/vision/landmark_utils.py`
if __name__ == "__main__":
    class FakeLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    test_landmarks = [FakeLandmark(i / 20.0, i / 30.0) for i in range(21)]
    features = normalize_landmarks(test_landmarks)
    
    assert features.shape == (FEATURE_VECTOR_SIZE,)
    assert features.dtype == np.float32
    print(f"Teste isolado passou! Shape {features.shape}, Dtype {features.dtype}")
