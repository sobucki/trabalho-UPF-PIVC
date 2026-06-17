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


def enhance_image_for_low_light(frame_bgr: np.ndarray) -> np.ndarray:
    """
    Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) 
    no canal L do espaço de cores LAB para realçar contornos 
    e ajudar na identificação em condições de baixa iluminação.
    """
    lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Clip limit de 3.0 e grid 8x8 costumam ser bons valores padrão
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    limg = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return enhanced_bgr

