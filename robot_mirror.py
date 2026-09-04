"""
robot_mirror.py
================
Main entry point for ROBOT MIRROR.

Opens two windows:
    1. "Camera"       - the live webcam feed with MediaPipe hand landmarks
                        drawn on top (for reference / debugging).
    2. "Robot Mirror" - a fully OpenCV-drawn futuristic robot that mirrors
                        the user's right hand in real time, with idle
                        breathing, blinking, a glowing sci-fi background,
                        and particle/trail effects.

Controls:
    ESC - quit
    D   - toggle debug overlay (joint markers, hand target crosshair, FPS)
    G   - toggle glow effects
    P   - toggle particle / trail effects

Run with:  python robot_mirror.py
"""

import math
import time

import cv2
import numpy as np

import config
from config import SKELETON
from hand_tracker import HandTracker
from animation import SignalSmoother, BlinkController, IdleAnimator, RobotPose
from effects import ParticleSystem, HandTrail
from background import Background
from robot import RobotRenderer
from utils import map_range, distance, clamp

class RobotMirrorApp:

    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam (index 0).")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        try:
            self.cap.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*"MJPG")
            )
        except Exception:
            pass
# ----------------------------------------
        self.hand_tracker = HandTracker(
            max_hands=config.MAX_NUM_HANDS,
            detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )

        self.smoother = SignalSmoother()
        self.blink = BlinkController()
        self.idle = IdleAnimator()
        self.particles = ParticleSystem(max_particles=config.MAX_PARTICLES)
        self.trail = HandTrail(length=config.HAND_TRAIL_LENGTH)
        self.background = Background(config.ROBOT_WIDTH, config.ROBOT_HEIGHT)
        self.renderer = RobotRenderer()

        # Toggles
        self.debug = False
        self.glow_enabled = True
        self.particles_enabled = True

        # Bookkeeping
        self._last_time = time.time()
        self._fps = 0.0
        self._last_wrist_px = None  # previous smoothed wrist position, for speed estimation

    # ----------------------------------------------------------------
    def run(self):
        try:
            while True:
                ok = self._step()
                if not ok:
                    break
        finally:
            self._cleanup()

    # ----------------------------------------------------------------
    def _step(self) -> bool:
        now = time.time()
        dt = max(now - self._last_time, 1e-4)
        self._last_time = now
        self._fps = self.smoother.smooth_scalar("fps", 1.0 / dt, 0.1)

        success, frame = self.cap.read()
        if not success:
            return False

        frame = cv2.flip(frame, 1)  # natural mirror view
        hand = self.hand_tracker.process(frame, draw_on=frame)

        pose = self._build_pose(hand, dt, now)

        robot_canvas = self.background.render(dt)
        self._update_effects(pose, dt)

        if self.particles_enabled and pose.hand_present:
            self.trail.draw(robot_canvas, config.CYAN)

        self.renderer.draw(robot_canvas, pose, glow_enabled=self.glow_enabled, debug=self.debug)

        if self.particles_enabled:
            self.particles.draw(robot_canvas)

        if self.debug:
            self._draw_hud(frame, robot_canvas)

        cv2.imshow(config.CAMERA_WINDOW_NAME, frame)
        cv2.imshow(config.ROBOT_WINDOW_NAME, robot_canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == config.KEY_ESC:
            return False
        elif key == config.KEY_DEBUG:
            self.debug = not self.debug
        elif key == config.KEY_GLOW:
            self.glow_enabled = not self.glow_enabled
        elif key == config.KEY_PARTICLES:
            self.particles_enabled = not self.particles_enabled
            if not self.particles_enabled:
                self.trail.clear()

        return True

    # ----------------------------------------------------------------
    def _build_pose(self, hand, dt: float, now: float) -> RobotPose:
        pose = RobotPose()

        idle_vals = self.idle.update(now)
        pose.breathing = idle_vals["breathing"]
        pose.sway = idle_vals["sway"]
        pose.head_bob = idle_vals["head_bob"]
        pose.head_tilt = idle_vals["head_tilt"]
        pose.eye_open = self.blink.update(now)

        if hand is None:
            pose.hand_present = False
            # Ease look direction and mood back to neutral rest state.
            pose.look_x = self.smoother.decay_toward("look_x", 0.0, 0.05)
            pose.look_y = self.smoother.decay_toward("look_y", 0.0, 0.05)
            pose.mood = "neutral"
            pose.finger_curls = {k: self.smoother.smooth_scalar(f"curl_{k}", 0.0, 0.15)
                                  for k in ("thumb", "index", "middle", "ring", "pinky")}
            self._last_wrist_px = None
            return pose

        pose.hand_present = True

        # Decide which side of the robot mirrors the hand based on which
        # half of the (already mirrored) camera frame the hand appears in -
        # this gives a natural "look in a mirror" mapping regardless of how
        # reliably MediaPipe's own Left/Right label holds up at odd angles.
        wrist_x_norm, wrist_y_norm = hand.wrist
        pose.active_side = "right" if wrist_x_norm > 0.5 else "left"

        sk = SKELETON
        shoulder_y = sk.torso_center[1] + sk.shoulder_drop
        target_x = map_range(wrist_x_norm, 0.0, 1.0, sk.head_radius, config.ROBOT_WIDTH - sk.head_radius)
        target_y = map_range(wrist_y_norm, 0.0, 1.0, shoulder_y - 60, config.ROBOT_HEIGHT - 140)
        raw_target = (target_x, target_y)

        smoothed_target = self.smoother.smooth_point("hand_target", raw_target, config.SMOOTH_ALPHA_POSITION)
        pose.hand_target = smoothed_target

        pose.wrist_angle = self.smoother.smooth_angle("wrist_angle", hand.palm_angle, config.SMOOTH_ALPHA_ANGLE)

        pose.finger_curls = {
            name: self.smoother.smooth_scalar(f"curl_{name}", curl, config.SMOOTH_ALPHA_FINGER)
            for name, curl in hand.finger_curls.items()
        }
        pose.openness = sum(pose.finger_curls.values()) / len(pose.finger_curls)
        pose.openness = 1.0 - pose.openness

        # Eyes look toward the hand's horizontal/vertical offset from center
        look_target_x = clamp((wrist_x_norm - 0.5) * 2.2, -1.0, 1.0)
        look_target_y = clamp((wrist_y_norm - 0.5) * 2.2, -1.0, 1.0)
        pose.look_x = self.smoother.smooth_scalar("look_x", look_target_x, 0.15)
        pose.look_y = self.smoother.smooth_scalar("look_y", look_target_y, 0.15)

        # Mood follows hand openness: open hand -> happy, fist -> surprised.
        if pose.openness > 0.7:
            pose.mood = "happy"
        elif pose.openness > 0.4:
            pose.mood = "smile"
        elif pose.openness < 0.15:
            pose.mood = "surprised"
        else:
            pose.mood = "neutral"

        self._track_speed_for_effects(smoothed_target)
        self._pending_target = smoothed_target
        return pose

    def _track_speed_for_effects(self, current_px):
        self._current_wrist_px = current_px

    # ----------------------------------------------------------------
    def _update_effects(self, pose: RobotPose, dt: float):
        self.particles.update(dt)

        if not pose.hand_present or pose.hand_target is None:
            self._last_wrist_px = None
            return

        current = pose.hand_target
        self.trail.push(current)

        if self._last_wrist_px is not None:
            speed = distance(self._last_wrist_px, current) / max(dt, 1e-4)
            if speed > 250 and self.particles_enabled:
                self.particles.spawn(current, config.PARTICLE_SPAWN_RATE, config.PARTICLE_COLOR, speed=speed * 0.3)
        self._last_wrist_px = current

    # ----------------------------------------------------------------
    def _draw_hud(self, camera_frame, robot_canvas):
        text = f"FPS: {self._fps:4.1f}"
        for canvas in (camera_frame, robot_canvas):
            cv2.putText(canvas, text, (14, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        config.CYAN, 2, lineType=cv2.LINE_AA)
        cv2.putText(robot_canvas, "DEBUG", (14, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    config.WARN_RED, 2, lineType=cv2.LINE_AA)

    # ----------------------------------------------------------------
    def _cleanup(self):
        self.cap.release()
        self.hand_tracker.close()
        cv2.destroyAllWindows()


def main():
    app = RobotMirrorApp()
    app.run()


if __name__ == "__main__":
    main()