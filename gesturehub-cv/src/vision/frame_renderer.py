from __future__ import annotations

from typing import Any
import cv2
import numpy as np

from src.vision.landmark_utils import HAND_CONNECTIONS


def landmarks_to_pixel_points(
    landmarks: Any,
    frame_width: int,
    frame_height: int,
) -> list[tuple[int, int]]:
    """
    Converte landmarks normalizados do MediaPipe para coordenadas de pixel.
    """
    if not landmarks:
        return []
        
    pts = []
    for lm in landmarks:
        if not hasattr(lm, 'x') or not hasattr(lm, 'y'):
            continue
        x = int(lm.x * frame_width)
        y = int(lm.y * frame_height)
        pts.append((x, y))
    return pts


def draw_landmarks(
    frame: np.ndarray,
    landmarks: Any,
    point_color: tuple[int, int, int] = (255, 255, 255),
    connection_color: tuple[int, int, int] = (0, 200, 0),
    point_radius: int = 4,
    connection_thickness: int = 2,
) -> np.ndarray:
    """
    Desenha os pontos da mão e suas conexões no frame.
    """
    if frame is None:
        raise ValueError("frame cannot be None")
    
    if not landmarks:
        return frame
        
    h, w = frame.shape[:2]
    points = landmarks_to_pixel_points(landmarks, w, h)
    
    if not points:
        return frame

    # Desenhar conexões
    for a, b in HAND_CONNECTIONS:
        if a < len(points) and b < len(points):
            cv2.line(frame, points[a], points[b], connection_color, connection_thickness)

    # Desenhar pontos
    for pt in points:
        cv2.circle(frame, pt, point_radius, point_color, -1)

    return frame


def draw_roi(
    frame: np.ndarray,
    top_left: tuple[int, int],
    bottom_right: tuple[int, int],
    label: str = "Área de controle da mão",
    color: tuple[int, int, int] = (255, 180, 0),
    thickness: int = 2,
) -> np.ndarray:
    """
    Desenha uma região de interesse (ROI) e um rótulo no frame.
    """
    if frame is None:
        raise ValueError("frame cannot be None")

    cv2.rectangle(frame, top_left, bottom_right, color, thickness)
    
    # Desenhar rótulo um pouco acima do retângulo
    text_pos = (top_left[0], max(0, top_left[1] - 10))
    draw_text(frame, label, text_pos, color=color, scale=0.5, thickness=1)
    
    return frame


def draw_text(
    frame: np.ndarray,
    text: str,
    position: tuple[int, int],
    color: tuple[int, int, int] = (255, 255, 255),
    scale: float = 0.6,
    thickness: int = 1,
) -> np.ndarray:
    """
    Centraliza o uso de cv2.putText para desenhar texto no frame.
    """
    if frame is None:
        raise ValueError("frame cannot be None")

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )
    return frame


def draw_status_overlay(
    frame: np.ndarray,
    gesture_name: str = "Nenhum",
    event_name: str = "-",
    status: str = "Aguardando gesto...",
    stable_frames: int | None = None,
    required_frames: int | None = None,
) -> np.ndarray:
    """
    Desenha um HUD visual de informações gerais para demonstração/debug.
    """
    if frame is None:
        raise ValueError("frame cannot be None")

    # Fundo semi-transparente do overlay
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 150), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    draw_text(frame, "GestureHub CV", (20, 35), color=(0, 255, 0), scale=0.7, thickness=2)
    draw_text(frame, f"Gesto: {gesture_name}", (20, 65))
    draw_text(frame, f"Evento: {event_name}", (20, 90))
    draw_text(frame, f"Status: {status}", (20, 115))
    
    if stable_frames is not None and required_frames is not None:
        draw_text(frame, f"Frames estaveis: {stable_frames}/{required_frames}", (20, 140))
        
    return frame


def draw_hand_bounding_box(
    frame: np.ndarray,
    landmarks: Any,
    color: tuple[int, int, int] = (0, 255, 255),
    thickness: int = 2,
    padding: int = 10,
) -> np.ndarray:
    """
    Desenha uma bounding box retangular englobando toda a mão detectada.
    """
    if frame is None:
        raise ValueError("frame cannot be None")

    if not landmarks:
        return frame

    h, w = frame.shape[:2]
    points = landmarks_to_pixel_points(landmarks, w, h)
    
    if not points:
        return frame

    min_x = max(0, min([pt[0] for pt in points]) - padding)
    min_y = max(0, min([pt[1] for pt in points]) - padding)
    max_x = min(w, max([pt[0] for pt in points]) + padding)
    max_y = min(h, max([pt[1] for pt in points]) + padding)

    cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), color, thickness)
    return frame


def render_final_frame(
    frame: np.ndarray,
    landmarks: Any = None,
    gesture_name: str = "Nenhum",
    event_name: str = "-",
    status: str = "Aguardando gesto...",
    stable_frames: int | None = None,
    required_frames: int | None = None,
) -> np.ndarray:
    """
    Função de alto nível que combina e renderiza todas as partes necessárias para gerar o frame final anotado.
    Faz uma cópia do frame antes de desenhar.
    """
    if frame is None:
        raise ValueError("frame cannot be None")

    output = frame.copy()

    if landmarks:
        draw_landmarks(output, landmarks)
        draw_hand_bounding_box(output, landmarks)

    draw_status_overlay(
        output, 
        gesture_name=gesture_name, 
        event_name=event_name, 
        status=status, 
        stable_frames=stable_frames, 
        required_frames=required_frames
    )

    return output

# Alias para compatibilidade temporal com a POC
desenhar_landmarks = draw_landmarks
