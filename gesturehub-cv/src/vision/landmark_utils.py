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
    coords_normalized = coords.copy()
    punho = coords_normalized[0]
    coords_normalized -= punho
    max_dist = np.max(np.linalg.norm(coords_normalized, axis=1))
    if max_dist == 0.0:
        max_dist = 1.0
    return coords_normalized / max_dist


def flatten_landmarks(coords: np.ndarray) -> np.ndarray:
    return coords.flatten().astype(np.float32)


def normalize_landmarks(landmarks: Sequence[Any]) -> np.ndarray:
    coords = landmarks_to_xy_array(landmarks)
    normalized_coords = normalize_xy_coordinates(coords)
    return flatten_landmarks(normalized_coords)
