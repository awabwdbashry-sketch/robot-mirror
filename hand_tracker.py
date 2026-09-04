"""
hand_tracker.py
================
Thin, well-documented wrapper around MediaPipe Hands that turns raw
landmark output into the higher-level features the animation system
actually needs: a wrist position, a palm-forward angle, and a 0..1
curl value for each of the five fingers.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

import cv2
import mediapipe as mp

Point = Tuple[float, float]

# MediaPipe hand landmark indices we care about
WRIST = 0
THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20


@dataclass
class HandData:
    """Everything downstream code needs about the currently tracked hand."""
    landmarks: List[Point]              # 21 normalized (x, y) points, [0, 1]
    handedness: str                     # "Right" / "Left" as reported by MediaPipe
    wrist: Point = field(init=False)
    palm_angle: float = field(init=False)   # radians, direction the hand is pointing
    openness: float = field(init=False)     # 0 (fist) .. 1 (fully open)
    finger_curls: Dict[str, float] = field(init=False)

    def __post_init__(self):
        self.wrist = self.landmarks[WRIST]
        middle_mcp = self.landmarks[MIDDLE_MCP]
        self.palm_angle = math.atan2(
            middle_mcp[1] - self.wrist[1], middle_mcp[0] - self.wrist[0]
        )
        self.finger_curls = self._compute_curls()
        self.openness = 1.0 - (sum(self.finger_curls.values()) / len(self.finger_curls))

    def _hand_scale(self) -> float:
        """A rough scale reference (wrist to middle-mcp distance) so curl
        estimates are resolution/distance independent."""
        wx, wy = self.wrist
        mx, my = self.landmarks[MIDDLE_MCP]
        return max(math.hypot(mx - wx, my - wy), 1e-4)

    def _curl_from_chain(self, mcp: int, pip: int, dip: int, tip: int) -> float:
        """
        Estimate curl by comparing the straight-line distance (wrist -> tip)
        against the fully extended path length (wrist->mcp->pip->dip->tip).
        A straight finger has a ratio near 1.0; a curled finger folds back
        toward the palm, shrinking the ratio toward ~0.4-0.5.
        """
        scale = self._hand_scale()
        w = self.wrist

        def d(a, b):
            return math.hypot(self.landmarks[a][0] - self.landmarks[b][0],
                               self.landmarks[a][1] - self.landmarks[b][1])

        path_len = d(WRIST, mcp) + d(mcp, pip) + d(pip, dip) + d(dip, tip)
        straight = math.hypot(self.landmarks[tip][0] - w[0], self.landmarks[tip][1] - w[1])
        if path_len < 1e-6:
            return 0.0
        ratio = straight / path_len
        # ratio ~0.95+ => extended (curl 0); ratio ~0.55 or below => curled (curl 1)
        curl = 1.0 - map_range_local(ratio, 0.55, 0.95, 0.0, 1.0)
        return clamp01(curl)

    def _curl_thumb(self) -> float:
        scale = self._hand_scale()

        def d(a, b):
            return math.hypot(self.landmarks[a][0] - self.landmarks[b][0],
                               self.landmarks[a][1] - self.landmarks[b][1])

        # Thumb curl approximated via distance from thumb tip to pinky-mcp
        # (a closed thumb tucks in toward the palm/pinky side).
        tip_to_pinky = d(THUMB_TIP, PINKY_MCP)
        ratio = tip_to_pinky / scale
        curl = 1.0 - map_range_local(ratio, 0.35, 1.3, 0.0, 1.0)
        return clamp01(curl)

    def _compute_curls(self) -> Dict[str, float]:
        return {
            "thumb": self._curl_thumb(),
            "index": self._curl_from_chain(INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP),
            "middle": self._curl_from_chain(MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP),
            "ring": self._curl_from_chain(RING_MCP, RING_PIP, RING_DIP, RING_TIP),
            "pinky": self._curl_from_chain(PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP),
        }


def clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


def map_range_local(x, in_min, in_max, out_min, out_max):
    if in_max - in_min == 0:
        return out_min
    t = (x - in_min) / (in_max - in_min)
    t = clamp01(t)
    return out_min + t * (out_max - out_min)


class HandTracker:
    """Wraps mediapipe.solutions.hands and exposes a simple process() API."""

    def __init__(self, max_hands: int = 1,
                 detection_confidence: float = 0.7,
                 tracking_confidence: float = 0.6):
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
             static_image_mode=False,          # فيديو مباشر وليس صور
             max_num_hands=1,                  # تتبع يد واحدة فقط
             model_complexity=0,               # أسرع نموذج
             min_detection_confidence=0.5,     # كافية لمعظم الاستخدامات
             min_tracking_confidence=0.5
       )    

    def process(self, frame_bgr, draw_on: Optional[any] = None) -> Optional[HandData]:
        """
        Runs detection on a BGR frame (already flipped for mirror view).
        If draw_on is given (a BGR image), the landmark skeleton is drawn
        onto it in-place (used for the debug Camera window).

        Prefers a hand MediaPipe labels "Right"; falls back to whatever
        hand was found if labelling is unavailable, since label accuracy
        degrades at odd angles and we would rather mirror *something*
        smoothly than drop tracking entirely.
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)

        if not results.multi_hand_landmarks:
            return None

        chosen_landmarks = results.multi_hand_landmarks[0]
        chosen_label = "Unknown"

        if results.multi_handedness:
            for lm, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                if label == "Right":
                    chosen_landmarks = lm
                    chosen_label = "Right"
                    break
            else:
                chosen_label = results.multi_handedness[0].classification[0].label

        if draw_on is not None:
            self._mp_draw.draw_landmarks(
                draw_on, chosen_landmarks, self._mp_hands.HAND_CONNECTIONS
            )

        points = [(lm.x, lm.y) for lm in chosen_landmarks.landmark]
        return HandData(landmarks=points, handedness=chosen_label)

    def close(self):
        self._hands.close()