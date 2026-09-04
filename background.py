"""
background.py
==============
Dark sci-fi backdrop for the Robot Mirror window: a vertical gradient,
a slowly scrolling perspective grid, sweeping light beams, and gently
rising ambient particles. All precomputed where possible so the per
frame cost stays low.
"""

import math
import random
import time
from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np

import config

Color = Tuple[int, int, int]


@dataclass
class _AmbientParticle:
    x: float
    y: float
    speed: float
    size: float
    twinkle_phase: float


class Background:
    """Renders the animated background into a fresh canvas each frame."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._gradient = self._build_gradient()
        self._t0 = time.time()
        self._particles = [self._new_particle(random_y=True) for _ in range(20)]

    # -- setup -------------------------------------------------------
    def _build_gradient(self) -> np.ndarray:
        grad = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        top = np.array(config.BG_TOP, dtype=np.float32)
        bottom = np.array(config.BG_BOTTOM, dtype=np.float32)
        for y in range(self.height):
            t = y / max(self.height - 1, 1)
            color = top + (bottom - top) * t
            grad[y, :, :] = color
        return grad

    def _new_particle(self, random_y: bool = False) -> _AmbientParticle:
        return _AmbientParticle(
            x=random.uniform(0, self.width),
            y=random.uniform(0, self.height) if random_y else self.height + random.uniform(0, 40),
            speed=random.uniform(12.0, 40.0),
            size=random.uniform(1.0, 2.6),
            twinkle_phase=random.uniform(0, 2 * math.pi),
        )

    # -- per-frame drawing --------------------------------------------
    def _draw_grid(self, canvas: np.ndarray, t: float):
        spacing = 70
        scroll = int((t * 22) % spacing)
        color = config.GRID_COLOR
        # Horizontal lines fading with a faint parallax scroll
        for y in range(-spacing, self.height + spacing, spacing):
            yy = y + scroll
            alpha = 0.18 + 0.10 * math.sin(yy * 0.02 + t)
            faded = tuple(int(c * alpha) for c in color)
            cv2.line(canvas, (0, yy), (self.width, yy), faded, 1, lineType=cv2.LINE_AA)
        # Vertical lines, static, faint
        for x in range(0, self.width, spacing):
            faded = tuple(int(c * 0.10) for c in color)
            cv2.line(canvas, (x, 0), (x, self.height), faded, 1, lineType=cv2.LINE_AA)

    def _draw_beams(self, canvas: np.ndarray, t: float):
        overlay = np.zeros_like(canvas)
        beam_count = 1
        for i in range(beam_count):
            phase = t * 0.15 + i * (2 * math.pi / beam_count)
            cx = (0.5 + 0.5 * math.sin(phase)) * self.width
            top_w = 60
            bottom_w = 220
            pts = np.array([
                [cx - top_w, 0],
                [cx + top_w, 0],
                [cx + bottom_w, self.height],
                [cx - bottom_w, self.height],
            ], dtype=np.int32)
            cv2.fillConvexPoly(overlay, pts, config.BEAM_COLOR, lineType=cv2.LINE_AA)
        # Disabled for better performance
        # overlay = cv2.GaussianBlur(overlay, (0, 0), sigmaX=35)
        cv2.addWeighted(canvas, 1.0, overlay, 0.06, 0, dst=canvas)

    def _update_and_draw_particles(self, canvas: np.ndarray, dt: float, t: float):
        for p in self._particles:
            p.y -= p.speed * dt
            if p.y < -10:
                new = self._new_particle(random_y=False)
                p.x, p.y, p.speed, p.size, p.twinkle_phase = new.x, new.y, new.speed, new.size, new.twinkle_phase
            twinkle = 0.5 + 0.5 * math.sin(t * 3 + p.twinkle_phase)
            color = tuple(int(c * (0.3 + 0.5 * twinkle)) for c in config.PARTICLE_COLOR)
            cv2.circle(canvas, (int(p.x), int(p.y)), max(int(p.size), 1), color, -1, lineType=cv2.LINE_AA)

    def render(self, dt: float) -> np.ndarray:
        t = time.time() - self._t0
        canvas = self._gradient.copy()
        self._draw_grid(canvas, t)
        self._draw_beams(canvas, t)
        self._update_and_draw_particles(canvas, dt, t)
        return canvas