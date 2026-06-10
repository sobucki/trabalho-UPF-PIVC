from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import TypedDict, Type

import cv2
import numpy as np

from src.config.paths import HAND_LANDMARKER_MODEL_PATH, GESTURE_SVM_MODEL_PATH
from src.vision.hand_landmarker_service import HandLandmarkerService
from src.vision.gesture_classifier import GestureClassifier
from src.vision.gesture_labels import (
    NO_GESTURE,
    get_default_action,
    get_event_name,
    get_gesture_name,
)
from src.vision.gesture_stabilizer import GestureStabilizer
from src.vision.frame_renderer import render_final_frame


class GesturePipelineResult(TypedDict):
    original_frame: np.ndarray
    rgb_frame: np.ndarray
    result_frame: np.ndarray
    landmarks_found: bool
    raw_label: int | None
    gesture: str
    event: str
    default_action: str
    confidence: str
    stable: bool
    triggered: bool
    in_cooldown: bool
    stable_frames: int
    required_frames: int
    cooldown_remaining: float
    cooldown: str
    status: str


class GesturePipeline:
    """
    Orquestrador central do pipeline de visão.
    Une captura de vídeo, o MediaPipe, SVM Classifier, Estabilizador
    e renderizador gráfico em um fluxo unidirecional limpo.
    """
    def __init__(
        self,
        hand_model_path: str | Path = HAND_LANDMARKER_MODEL_PATH,
        svm_model_path: str | Path = GESTURE_SVM_MODEL_PATH,
        frames_required: int = 5,
        cooldown_seconds: float = 1.2,
    ) -> None:
        self.hand_model_path = Path(hand_model_path)
        self.svm_model_path = Path(svm_model_path)
        
        self.hand_landmarker = HandLandmarkerService(self.hand_model_path)
        self.classifier = GestureClassifier(self.svm_model_path)
        self.stabilizer = GestureStabilizer(
            frames_required=frames_required,
            cooldown_seconds=cooldown_seconds,
        )
        self._started = False

    @property
    def is_started(self) -> bool:
        return self._started

    def start(self) -> None:
        if self._started:
            return

        self.hand_landmarker.start()
        self._started = True

    def close(self) -> None:
        self.hand_landmarker.close()
        self.stabilizer.reset()
        self._started = False

    def reset(self) -> None:
        self.stabilizer.reset()

    def __enter__(self) -> "GesturePipeline":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _validate_frame(self, frame_bgr: np.ndarray) -> np.ndarray:
        if frame_bgr is None:
            raise ValueError("frame_bgr must be a valid BGR image with shape (height, width, 3).")
        if not isinstance(frame_bgr, np.ndarray):
            raise ValueError("frame_bgr must be a valid BGR image with shape (height, width, 3).")
        if frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
            raise ValueError("frame_bgr must be a valid BGR image with shape (height, width, 3).")
        return np.ascontiguousarray(frame_bgr)

    def _get_status_text(self, stabilizer_status: str, landmarks_found: bool) -> str:
        if stabilizer_status == "NO_GESTURE":
            return "Nenhum gesto reconhecido" if landmarks_found else "Sem mao detectada"
        elif stabilizer_status == "DETECTING":
            return "Detectando gesto"
        elif stabilizer_status == "TRIGGERED":
            return "Evento pronto"
        elif stabilizer_status == "COOLDOWN":
            return "Cooldown"
        return stabilizer_status

    def _format_cooldown(self, cooldown_remaining: float) -> str:
        if cooldown_remaining <= 0:
            return "Pronto"
        return f"{cooldown_remaining:.1f}s"

    def _format_confidence(self, stable_frames: int, required_frames: int) -> str:
        return f"{stable_frames}/{required_frames}"

    def _build_result(
        self,
        original_frame: np.ndarray,
        rgb_frame: np.ndarray,
        result_frame: np.ndarray,
        landmarks_found: bool,
        raw_label: int | None,
        gesture: str,
        event: str,
        default_action: str,
        stabilizer_result: dict,
    ) -> GesturePipelineResult:
        return {
            "original_frame": original_frame,
            "rgb_frame": rgb_frame,
            "result_frame": result_frame,
            "landmarks_found": landmarks_found,
            "raw_label": raw_label,
            "gesture": gesture,
            "event": event,
            "default_action": default_action,
            "confidence": self._format_confidence(
                stabilizer_result["stable_frames"],
                stabilizer_result["required_frames"],
            ),
            "stable": stabilizer_result["stable"],
            "triggered": stabilizer_result["triggered"],
            "in_cooldown": stabilizer_result["in_cooldown"],
            "stable_frames": stabilizer_result["stable_frames"],
            "required_frames": stabilizer_result["required_frames"],
            "cooldown_remaining": stabilizer_result["cooldown_remaining"],
            "cooldown": self._format_cooldown(stabilizer_result["cooldown_remaining"]),
            "status": self._get_status_text(stabilizer_result["status"], landmarks_found),
        }

    def process_frame(self, frame_bgr: np.ndarray, timestamp_ms: int) -> GesturePipelineResult:
        if not self.is_started:
            raise RuntimeError("GesturePipeline must be started before processing frames.")

        frame_bgr = self._validate_frame(frame_bgr)
        original_frame = frame_bgr.copy()
        
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        mp_result = self.hand_landmarker.detect(rgb_frame, timestamp_ms)
        
        if mp_result.hand_landmarks:
            landmarks = mp_result.hand_landmarks[0]
            raw_label = self.classifier.predict_from_landmarks(landmarks)
            
            gesture = get_gesture_name(raw_label)
            event = get_event_name(raw_label)
            default_action = get_default_action(raw_label)
            
            stabilizer_result = self.stabilizer.update(raw_label)
            
            status_text = self._get_status_text(stabilizer_result["status"], True)
            
            result_frame = render_final_frame(
                frame=frame_bgr,
                landmarks=landmarks,
                gesture_name=gesture,
                event_name=event,
                status=status_text,
                stable_frames=stabilizer_result["stable_frames"],
                required_frames=stabilizer_result["required_frames"],
            )
            
            return self._build_result(
                original_frame=original_frame,
                rgb_frame=rgb_frame,
                result_frame=result_frame,
                landmarks_found=True,
                raw_label=raw_label,
                gesture=gesture,
                event=event,
                default_action=default_action,
                stabilizer_result=stabilizer_result,
            )
        else:
            stabilizer_result = self.stabilizer.update(None)
            
            raw_label = None
            gesture = "Nenhum"
            event = NO_GESTURE
            default_action = "Nenhuma ação"
            
            status_text = self._get_status_text(stabilizer_result["status"], False)
            
            result_frame = render_final_frame(
                frame=frame_bgr,
                landmarks=None,
                gesture_name=gesture,
                event_name=event,
                status=status_text,
                stable_frames=stabilizer_result["stable_frames"],
                required_frames=stabilizer_result["required_frames"],
            )
            
            return self._build_result(
                original_frame=original_frame,
                rgb_frame=rgb_frame,
                result_frame=result_frame,
                landmarks_found=False,
                raw_label=raw_label,
                gesture=gesture,
                event=event,
                default_action=default_action,
                stabilizer_result=stabilizer_result,
            )
