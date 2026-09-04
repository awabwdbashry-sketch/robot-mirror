"""
effects.py
==========
Visual polish layer: additive glow rendering, a hand-motion particle
spark system, a fading hand trail, and a soft drop-shadow helper.
None of these know anything about robot anatomy - they operate purely
on canvases, points and colors, so they can be reused for background
effects too.
"""

import math
import random
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

import cv2
import numpy as np

Point = Tuple[float, float]
Color = Tuple[int, int, int]


class GlowRenderer:
    """
    Fakes a neon glow using OpenCV's additive blending: draw the shape
    several times on a transparent-ish overlay at increasing thickness
    and decreasing opacity, blur it, then screen-blend onto the canvas.
    This avoids any dependency on GPU shaders while still giving a
    convincing soft glow around robot edges and eyes.
    """

    def __init__(self, layers: int = 1):
        self.layers = layers

    def glow_circle(self, canvas: np.ndarray, center: Point, radius: int, color: Color,
                     intensity: float = 1.0):
        overlay = np.zeros_like(canvas)
        c = (int(center[0]), int(center[1]))
        for i in range(self.layers, 0, -1):
            r = int(radius * (1.0 + i * 0.55))
            alpha = (intensity * 0.35) / i
            cv2.circle(overlay, c, max(r, 1), color, -1, lineType=cv2.LINE_AA)
            cv2.addWeighted(canvas, 1.0, overlay, alpha * 0.5, 0, dst=canvas)
            overlay[:] = 0

    def glow_line(self, canvas: np.ndarray, p1: Point, p2: Point, thickness: int,
                   color: Color, intensity: float = 0.8):
        overlay = np.zeros_like(canvas)
        p1i = (int(p1[0]), int(p1[1]))
        p2i = (int(p2[0]), int(p2[1]))
        for i in range(self.layers, 0, -1):
            t = int(thickness * (1.0 + i * 0.7))
            alpha = (intensity * 0.30) / i
            cv2.line(overlay, p1i, p2i, color, t, lineType=cv2.LINE_AA)
        cv2.addWeighted(canvas, 1.0, overlay, intensity * 0.3, 0, dst=canvas)


@dataclass
class Particle:
    pos: List[float]
    vel: List[float]
    life: float
    max_life: float
    size: float
    color: Color


class ParticleSystem:
    """Small spark particles that burst from the hand when it moves quickly."""

    def __init__(self, max_particles: int = 40):
        self.max_particles = max_particles
        self._particles: List[Particle] = []

    def spawn(self, origin: Point, count: int, color: Color, speed: float = 90.0):
        count = min(count, 5)
        for _ in range(count):
            if len(self._particles) >= self.max_particles:
                break
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.2, 1.0) * speed
            life = random.uniform(0.35, 0.9)
            self._particles.append(Particle(
                pos=[origin[0], origin[1]],
                vel=[math.cos(angle) * spd, math.sin(angle) * spd],
                life=life,
                max_life=life,
                size=random.uniform(2.0, 4.5),
                color=color,
            ))

    def update(self, dt: float):
        alive = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.pos[0] += p.vel[0] * dt
            p.pos[1] += p.vel[1] * dt
            p.vel[0] *= 0.94
            p.vel[1] *= 0.94
            alive.append(p)
        self._particles = alive

    def draw(self, canvas: np.ndarray):
        for p in self._particles:
            t = p.life / p.max_life
            color = tuple(int(c * t) for c in p.color)
            center = (int(p.pos[0]), int(p.pos[1]))
            cv2.circle(canvas, center, max(int(p.size * t), 1), color, -1, lineType=cv2.LINE_AA)


class HandTrail:
    """Fading trail of recent hand positions, giving a sense of motion."""

    def __init__(self, length: int = 8):
        self._points: Deque[Point] = deque(maxlen=length)

    def push(self, point: Point):
        self._points.append(point)

    def clear(self):
        self._points.clear()

    def draw(self, canvas: np.ndarray, color: Color):
        n = len(self._points)
        if n < 2:
            return
        pts = list(self._points)
        for i in range(1, n):
            t = i / n
            thickness = max(1, int(t * 8))
            faded = tuple(int(c * (0.15 + 0.5 * t)) for c in color)
            p1 = (int(pts[i - 1][0]), int(pts[i - 1][1]))
            p2 = (int(pts[i][0]), int(pts[i][1]))
            cv2.line(canvas, p1, p2, faded, thickness, lineType=cv2.LINE_AA)


def draw_soft_shadow(canvas: np.ndarray, center: Point, size: Tuple[int, int], color: Color = (0, 0, 0)):
    """Draws a soft elliptical shadow beneath a body part (e.g. feet)."""
    overlay = canvas.copy()
    c = (int(center[0]), int(center[1]))
    cv2.ellipse(overlay, c, size, 0, 0, 360, color, -1, lineType=cv2.LINE_AA)
    # GaussianBlur removed for better performance
    cv2.addWeighted(canvas, 0.75, overlay, 0.25, 0, dst=canvas)