"""
utils.py
========
Small, dependency-free math helpers shared across the project:
interpolation, EMA smoothing, vector math, and analytic two-link
inverse kinematics.
"""

import math
from typing import Tuple

Point = Tuple[float, float]


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to the inclusive range [lo, hi]."""
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b at t in [0, 1]."""
    return a + (b - a) * t


def ema(previous: float, new: float, alpha: float) -> float:
    """
    Exponential moving average smoothing.
    alpha close to 1.0 -> snappy / trusts new value more.
    alpha close to 0.0 -> heavily smoothed / laggy but stable.
    """
    return previous + alpha * (new - previous)


def ema_point(previous: Point, new: Point, alpha: float) -> Point:
    return (ema(previous[0], new[0], alpha), ema(previous[1], new[1], alpha))


def distance(p1: Point, p2: Point) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def map_range(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Map x from [in_min, in_max] into [out_min, out_max], with clamping."""
    if in_max - in_min == 0:
        return out_min
    t = (x - in_min) / (in_max - in_min)
    t = clamp(t, 0.0, 1.0)
    return out_min + t * (out_max - out_min)


def angle_of(p_from: Point, p_to: Point) -> float:
    """Angle (radians) of the vector from p_from to p_to, standard math convention."""
    return math.atan2(p_to[1] - p_from[1], p_to[0] - p_from[0])


def point_along(origin: Point, angle: float, length: float) -> Point:
    """Point at `length` from origin, along `angle` radians."""
    return (origin[0] + math.cos(angle) * length, origin[1] + math.sin(angle) * length)


def normalize_angle(angle: float) -> float:
    """Wrap an angle (radians) into (-pi, pi]."""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle <= -math.pi:
        angle += 2 * math.pi
    return angle


def lerp_angle(a: float, b: float, t: float) -> float:
    """Interpolate between two angles taking the shortest path."""
    diff = normalize_angle(b - a)
    return a + diff * t


def two_link_ik(shoulder: Point, target: Point, l1: float, l2: float,
                 bend_sign: float = 1.0):
    """
    Analytic 2-bone inverse kinematics (law of cosines), the classic
    "shoulder -> elbow -> wrist" solve used throughout robotics and
    skeletal animation.

    Returns (shoulder_angle, elbow_bend_angle, elbow_point, wrist_point)
    where shoulder_angle is the absolute angle of the upper segment,
    and elbow_bend_angle is the *relative* bend at the elbow (0 = straight).

    bend_sign flips which way the elbow bends (+1 / -1) so left/right
    arms bend naturally instead of mirroring incorrectly.
    """
    dx = target[0] - shoulder[0]
    dy = target[1] - shoulder[1]
    dist = math.hypot(dx, dy)
    max_reach = l1 + l2
    min_reach = abs(l1 - l2) + 1e-3

    dist_clamped = clamp(dist, min_reach, max_reach * 0.999)

    # Angle of the direct line from shoulder to target
    base_angle = math.atan2(dy, dx)

    # Law of cosines: angle at the shoulder between the direct line and l1
    cos_a = (l1 ** 2 + dist_clamped ** 2 - l2 ** 2) / (2 * l1 * dist_clamped)
    cos_a = clamp(cos_a, -1.0, 1.0)
    a = math.acos(cos_a)

    # Law of cosines: interior angle at the elbow
    cos_b = (l1 ** 2 + l2 ** 2 - dist_clamped ** 2) / (2 * l1 * l2)
    cos_b = clamp(cos_b, -1.0, 1.0)
    b = math.acos(cos_b)

    shoulder_angle = base_angle + bend_sign * a
    elbow_bend = math.pi - b  # 0 when fully extended

    elbow_point = point_along(shoulder, shoulder_angle, l1)
    forearm_angle = shoulder_angle - bend_sign * elbow_bend
    wrist_point = point_along(elbow_point, forearm_angle, l2)

    return shoulder_angle, forearm_angle, elbow_point, wrist_point


def draw_capsule(canvas, p1: Point, p2: Point, thickness: int, color, cv2_module):
    """
    Draw a capsule (thick line with round caps) between p1 and p2.
    This is the basic building block used for every robot limb, giving
    the "rounded modern" look requested without needing external assets.
    """
    p1i = (int(round(p1[0])), int(round(p1[1])))
    p2i = (int(round(p2[0])), int(round(p2[1])))
    cv2_module.line(canvas, p1i, p2i, color, thickness, lineType=cv2_module.LINE_AA)
    r = thickness // 2
    cv2_module.circle(canvas, p1i, r, color, -1, lineType=cv2_module.LINE_AA)
    cv2_module.circle(canvas, p2i, r, color, -1, lineType=cv2_module.LINE_AA)