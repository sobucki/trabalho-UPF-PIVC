from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap


def cv_frame_to_qpixmap(frame_bgr: np.ndarray) -> QPixmap:
    """
    Converte um frame do OpenCV (BGR) para QPixmap para exibicao no PySide6.
    """
    if frame_bgr is None:
        raise ValueError("frame_bgr cannot be None.")

    if not isinstance(frame_bgr, np.ndarray):
        raise ValueError("frame_bgr must be a numpy.ndarray.")

    if frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
        raise ValueError("frame_bgr must have shape (height, width, 3).")

    # Converter BGR para RGB
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    
    # Garantir um array contíguo na memoria
    frame_rgb = np.ascontiguousarray(frame_rgb)

    height, width, channels = frame_rgb.shape
    bytes_per_line = channels * width

    # O formato Format_RGB888 e o correto para imagens de 3 canais de 8 bits
    image = QImage(
        frame_rgb.data,
        width,
        height,
        bytes_per_line,
        QImage.Format.Format_RGB888,
    )

    return QPixmap.fromImage(image.copy())
