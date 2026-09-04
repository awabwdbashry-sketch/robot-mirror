"""
config.py
=========
Central configuration for the Robot Mirror application.

Every tunable constant lives here: window sizes, the robot's skeletal
proportions, its color palette, smoothing factors, and key bindings.
Keeping these in one place makes the rest of the codebase free of
"magic numbers" and easy to re-tune.
"""

from dataclasses import dataclass, field
from typing import Tuple

Color = Tuple[int, int, int]  # BGR, as OpenCV expects

# --------------------------------------------------------------------------
# Window / canvas geometry
# --------------------------------------------------------------------------
CAMERA_WINDOW_NAME = "Camera"
ROBOT_WINDOW_NAME = "Robot Mirror"

ROBOT_WIDTH = 820
ROBOT_HEIGHT = 920

FPS_TARGET = 60

# --------------------------------------------------------------------------
# Color palette (BGR order for OpenCV)
# --------------------------------------------------------------------------
DARK_GRAY: Color = (38, 38, 40)
GRAY: Color = (70, 70, 74)
SILVER: Color = (196, 196, 200)
CYAN: Color = (255, 255, 0)
BLUE_NEON: Color = (255, 110, 20)
DEEP_BLUE: Color = (120, 40, 10)
EYE_GLOW: Color = (255, 250, 170)
WARN_RED: Color = (60, 60, 220)

BG_TOP: Color = (25, 12, 8)
BG_BOTTOM: Color = (5, 3, 2)
GRID_COLOR: Color = (90, 45, 10)
BEAM_COLOR: Color = (255, 180, 90)
PARTICLE_COLOR: Color = (255, 220, 140)

# --------------------------------------------------------------------------
# Key bindings
# --------------------------------------------------------------------------
KEY_ESC = 27
KEY_DEBUG = ord('d')
KEY_GLOW = ord('g')
KEY_PARTICLES = ord('p')

# --------------------------------------------------------------------------
# Robot skeleton proportions (pixels, in ROBOT canvas space)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Skeleton:
    torso_w: float = 210.0
    torso_h: float = 260.0
    torso_center: Tuple[float, float] = (ROBOT_WIDTH / 2, ROBOT_HEIGHT * 0.46)

    neck_len: float = 34.0
    head_radius: float = 72.0

    shoulder_offset_x: float = 132.0
    shoulder_drop: float = -110.0  # relative to torso_center.y

    upper_arm_len: float = 148.0
    forearm_len: float = 132.0
    hand_len: float = 58.0

    hip_offset_x: float = 76.0
    hip_drop: float = 130.0  # relative to torso_center.y

    thigh_len: float = 176.0
    shin_len: float = 156.0
    foot_len: float = 52.0

    limb_thickness: int = 34
    forearm_thickness: int = 26
    finger_thickness: int = 10


SKELETON = Skeleton()

# Finger segment lengths: (base->pip, pip->dip, dip->tip). Thumb has 2 segments.
FINGER_SEGMENTS = {
    "thumb": (30.0, 24.0),
    "index": (34.0, 24.0, 18.0),
    "middle": (38.0, 27.0, 20.0),
    "ring": (35.0, 25.0, 18.0),
    "pinky": (28.0, 20.0, 16.0),
}

# Angular spread (radians) of each finger base around the hand's forward axis
FINGER_SPREAD = {
    "thumb": -1.05,
    "index": -0.32,
    "middle": -0.08,
    "ring": 0.16,
    "pinky": 0.40,
}

MAX_FINGER_BEND = 1.55  # radians per joint at full curl (curl == 1.0)

# --------------------------------------------------------------------------
# Smoothing (EMA alpha values, higher = snappier / less smoothing)
# --------------------------------------------------------------------------
SMOOTH_ALPHA_POSITION = 0.35
SMOOTH_ALPHA_ANGLE = 0.30
SMOOTH_ALPHA_FINGER = 0.40

# --------------------------------------------------------------------------
# Hand tracking
# --------------------------------------------------------------------------
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.6

# --------------------------------------------------------------------------
# Effects
# --------------------------------------------------------------------------
MAX_PARTICLES = 120
PARTICLE_SPAWN_RATE = 4          # particles spawned per frame while hand moves
HAND_TRAIL_LENGTH = 14
GLOW_LAYERS = 3