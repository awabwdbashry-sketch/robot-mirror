"""
animation.py
============
Everything related to *how the robot moves over time* rather than how
it is drawn: EMA smoothing of noisy tracking signals, a random blink
scheduler, idle breathing/floating motion, and the RobotPose container
that ties a frame's worth of animation state together.
"""

import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from utils import ema, ema_point, lerp_angle

Point = Tuple[float, float]


class SignalSmoother:
    """
    Generic exponential-moving-average smoother for named scalar and
    point signals. Keeping this as one object (rather than scattering
    "prev_x" variables everywhere) makes the main loop much cleaner and
    guarantees every tracked value is initialized lazily on first use.
    """

    def __init__(self):
        self._scalars: Dict[str, float] = {}
        self._points: Dict[str, Point] = {}

    def smooth_scalar(self, name: str, value: float, alpha: float) -> float:
        if name not in self._scalars:
            self._scalars[name] = value
        else:
            self._scalars[name] = ema(self._scalars[name], value, alpha)
        return self._scalars[name]

    def smooth_angle(self, name: str, value: float, alpha: float) -> float:
        if name not in self._scalars:
            self._scalars[name] = value
        else:
            self._scalars[name] = lerp_angle(self._scalars[name], value, alpha)
        return self._scalars[name]

    def smooth_point(self, name: str, value: Point, alpha: float) -> Point:
        if name not in self._points:
            self._points[name] = value
        else:
            self._points[name] = ema_point(self._points[name], value, alpha)
        return self._points[name]

    def decay_toward(self, name: str, target: float, alpha: float) -> float:
        """Same as smooth_scalar but reads intent clearly at call sites
        that are easing a value back to a rest state (e.g. no hand found)."""
        return self.smooth_scalar(name, target, alpha)


class BlinkController:
    """Schedules natural, irregular eye blinks."""

    def __init__(self):
        self._next_blink_at = time.time() + random.uniform(2.0, 5.0)
        self._blink_start: Optional[float] = None
        self._blink_duration = 0.14

    def update(self, now: float) -> float:
        """Returns eye-open amount in [0, 1] (1 = fully open)."""
        if self._blink_start is None:
            if now >= self._next_blink_at:
                self._blink_start = now
            return 1.0

        t = (now - self._blink_start) / self._blink_duration
        if t >= 1.0:
            self._blink_start = None
            self._next_blink_at = now + random.uniform(2.0, 6.0)
            return 1.0

        # Triangle wave: closes then opens within the blink duration.
        openness = 1.0 - math.sin(min(t, 1.0) * math.pi)
        return max(0.0, openness)


class IdleAnimator:
    """
    Produces subtle, continuous idle motion so the robot never looks
    frozen: breathing (torso scale), a slow idle sway, and a gentle
    head bob. All driven by sine waves at different, non-resonant
    frequencies so the motion never looks mechanically repetitive.
    """

    def __init__(self):
        self._t0 = time.time()

    def update(self, now: float) -> Dict[str, float]:
        t = now - self._t0
        breathing = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 4.2)   # ~4.2s cycle
        sway = math.sin(t * 2 * math.pi / 7.0)                    # slow left/right
        head_bob = math.sin(t * 2 * math.pi / 3.1)
        head_tilt = math.sin(t * 2 * math.pi / 9.3) * 0.06
        return {
            "breathing": breathing,       # 0..1
            "sway": sway,                 # -1..1
            "head_bob": head_bob,         # -1..1
            "head_tilt": head_tilt,       # small radians
        }


@dataclass
class RobotPose:
    """A single frame's worth of resolved robot animation state."""
    hand_present: bool = False

    # Arm target in ROBOT canvas coordinates (None if no hand tracked)
    hand_target: Optional[Point] = None
    active_side: str = "right"       # "right" or "left" - which arm mirrors the hand
    wrist_angle: float = 0.0
    finger_curls: Dict[str, float] = field(default_factory=lambda: {
        "thumb": 0.0, "index": 0.0, "middle": 0.0, "ring": 0.0, "pinky": 0.0
    })
    openness: float = 1.0

    # Idle state
    breathing: float = 0.5
    sway: float = 0.0
    head_bob: float = 0.0
    head_tilt: float = 0.0

    # Face
    eye_open: float = 1.0
    look_x: float = 0.0     # -1..1
    look_y: float = 0.0     # -1..1
    mood: str = "neutral"   # "neutral" | "smile" | "happy" | "surprised"