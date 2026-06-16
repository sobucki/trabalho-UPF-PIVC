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

