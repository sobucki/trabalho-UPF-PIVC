from __future__ import annotations

import time
from typing import TypedDict


STATUS_NO_GESTURE = "NO_GESTURE"
STATUS_DETECTING = "DETECTING"
STATUS_TRIGGERED = "TRIGGERED"
STATUS_COOLDOWN = "COOLDOWN"


class StabilizerResult(TypedDict):
    label: int | None
    stable: bool
    triggered: bool
    in_cooldown: bool
    stable_frames: int
    required_frames: int
    cooldown_remaining: float
    status: str


class GestureStabilizer:
    """
    Rastreia a estabilidade de detecção de gestos em múltiplos frames para evitar 
    disparos erráticos e implementa cooldown pós-disparo.
    """

    def __init__(
        self,
        frames_required: int = 5,
        cooldown_seconds: float = 1.2,
        no_gesture_label: int | None = None,
    ) -> None:
        if frames_required <= 0:
            raise ValueError("frames_required must be greater than zero.")
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds cannot be negative.")

        self.frames_required = frames_required
        self.cooldown_seconds = cooldown_seconds
        self.no_gesture_label = no_gesture_label

        self._last_label: int | None = None
        self._consecutive_frames: int = 0
        self._last_triggered_label: int | None = None
        # Para evitar falso cooldown caso time.monotonic() comece próximo de 0
        self._last_triggered_at: float = -float('inf')

    @property
    def consecutive_frames(self) -> int:
        return self._consecutive_frames

    @property
    def last_label(self) -> int | None:
        return self._last_label

    @property
    def last_triggered_label(self) -> int | None:
        return self._last_triggered_label

    def _normalize_label(self, gesture_label: int | None) -> int | None:
        """Trata valores de ausência (-1, no_gesture_label) como None."""
        if gesture_label is None:
            return None
        if gesture_label == -1:
            return None
        if gesture_label == self.no_gesture_label:
            return None
        return gesture_label

    def _get_cooldown_remaining(self, now: float | None = None) -> float:
        """Retorna os segundos remanescentes do último disparo."""
        if now is None:
            now = time.monotonic()
        elapsed = now - self._last_triggered_at
        if elapsed >= self.cooldown_seconds:
            return 0.0
        return self.cooldown_seconds - elapsed

    def _is_in_cooldown(self, now: float | None = None) -> bool:
        """Verifica se ainda estamos sob a janela de cooldown."""
        return self._get_cooldown_remaining(now) > 0.0

    def _build_result(
        self,
        label: int | None,
        stable: bool,
        triggered: bool,
        in_cooldown: bool,
        status: str,
        cooldown_remaining: float = 0.0,
    ) -> StabilizerResult:
        return {
            "label": label,
            "stable": stable,
            "triggered": triggered,
            "in_cooldown": in_cooldown,
            "stable_frames": self._consecutive_frames,
            "required_frames": self.frames_required,
            "cooldown_remaining": cooldown_remaining,
            "status": status,
        }

    def reset(self) -> None:
        """Limpa todo o estado do estabilizador (útil ao desligar a câmera/trocar aba)."""
        self._last_label = None
        self._consecutive_frames = 0
        self._last_triggered_label = None
        self._last_triggered_at = -float('inf')

    def force_cooldown(self) -> None:
        """Força o início imediato de um cooldown artificial."""
        self._last_triggered_at = time.monotonic()

    def update(self, gesture_label: int | None) -> StabilizerResult:
        """
        Processa o label atual da inferência, acumula estado de estabilidade
        e retorna a instrução de ação segura para a aplicação.
        """
        now = time.monotonic()
        normalized_label = self._normalize_label(gesture_label)

        # Sem Gesto detectado
        if normalized_label is None:
            self._consecutive_frames = 0
            self._last_label = None
            
            in_cooldown = self._is_in_cooldown(now)
            cooldown_rem = self._get_cooldown_remaining(now) if in_cooldown else 0.0
            
            status = STATUS_COOLDOWN if in_cooldown else STATUS_NO_GESTURE
            
            return self._build_result(
                label=None,
                stable=False,
                triggered=False,
                in_cooldown=in_cooldown,
                status=status,
                cooldown_remaining=cooldown_rem,
            )

        # Processamento do Gesto
        if normalized_label == self._last_label:
            self._consecutive_frames += 1
        else:
            self._last_label = normalized_label
            self._consecutive_frames = 1

        stable = self._consecutive_frames >= self.frames_required
        in_cooldown = self._is_in_cooldown(now)
        cooldown_rem = self._get_cooldown_remaining(now)

        # Se estabilizou mas estamos em cooldown, apenas avisamos e seguramos
        if stable and in_cooldown:
            return self._build_result(
                label=normalized_label,
                stable=True,
                triggered=False,
                in_cooldown=True,
                status=STATUS_COOLDOWN,
                cooldown_remaining=cooldown_rem,
            )

        # Se estabilizou e NÃO estamos em cooldown: DISPARAR (Estratégia A)
        if stable and not in_cooldown:
            # Marcamos o evento como executado
            self._last_triggered_label = normalized_label
            self._last_triggered_at = now
            
            result = self._build_result(
                label=normalized_label,
                stable=True,
                triggered=True,
                in_cooldown=False,
                status=STATUS_TRIGGERED,
                cooldown_remaining=0.0,
            )
            
            # Resetamos a contagem para forçar nova detecção longa do zero se a mão ficar parada (Estratégia A)
            self._consecutive_frames = 0
            self._last_label = None
            
            return result

        # Detectando (Não estável ainda)
        return self._build_result(
            label=normalized_label,
            stable=False,
            triggered=False,
            in_cooldown=in_cooldown,
            status=STATUS_DETECTING,
            cooldown_remaining=cooldown_rem,
        )
