from __future__ import annotations

import cv2
import numpy as np


def validate_bgr_frame(frame_bgr: np.ndarray) -> np.ndarray:
    """Valida e retorna um frame contíguo."""
    if frame_bgr is None:
        raise ValueError("frame_bgr cannot be None.")
    if not isinstance(frame_bgr, np.ndarray):
        raise ValueError("frame_bgr must be a numpy.ndarray.")
    if frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
        raise ValueError("frame_bgr must be a valid BGR image with shape (height, width, 3).")
    return np.ascontiguousarray(frame_bgr)


def create_hsv_frame(frame_bgr: np.ndarray) -> np.ndarray:
    """Converte o frame para o espaço HSV e o retorna visualizável (BGR)."""
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    hsv_as_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return hsv_as_bgr


def create_threshold_mask_frame(frame_bgr: np.ndarray) -> np.ndarray:
    """Gera uma máscara binária e a converte de volta para 3 canais (BGR)."""
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    return mask_bgr


def create_contours_frame(frame_bgr: np.ndarray, landmarks=None) -> np.ndarray:
    """
    Retorna uma visualização estrutural:
    Se houver landmarks, desenha as conexões de mão.
    Se não, desenha as bordas de Canny.
    """
    from src.vision.frame_renderer import render_final_frame

    if landmarks is not None:
        # Usa o render_final_frame apenas para desenhar os landmarks na cópia, sem textos
        return render_final_frame(
            frame=frame_bgr.copy(),
            landmarks=landmarks,
            gesture_name="",
            event_name="",
            status="",
            stable_frames=0,
            required_frames=1,
        )
    else:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return edges_bgr
