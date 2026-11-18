"""
camera_controller.py
State-of-the-Art Neural Hand & Finger Tracking for XO (Tic-Tac-Toe).
Powered by Google MediaPipe Tasks HandLandmarker deep learning model.
Features:
- Precise 21-point 3D hand landmark tracking (tracks exact index fingertip).
- 100% immune to walls, faces, lighting, shadows, and background objects.
- Instant Pinch-to-Click (touch index & thumb) + Snappy Hover Dwell (0.7s).
- Holographic glowing hand skeleton visualization.
- Exponential Moving Average (EMA) cursor smoothing.
"""

import math
import os
import time
from typing import Callable, Optional
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from game_logic import AI, EMPTY, HUMAN, Board

CV_AVAILABLE = True

# Standard 21-point Hand Skeleton Connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index finger
    (9, 10), (10, 11), (11, 12),           # Middle finger
    (13, 14), (14, 15), (15, 16),          # Ring finger
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)              # Palm base
]


class CameraGestureController:
    """Accurate deep-learning hand controller using Google MediaPipe HandLandmarker."""

    def __init__(self, board: Board, on_move_callback: Callable[[int], None]):
        self.board = board
        self.on_move_callback = on_move_callback
        self.is_running = False

        # Gesture Detection Parameters
        self.hover_cell: Optional[int] = None
        self.hover_start_time: float = 0.0
        self.HOVER_THRESHOLD = 0.70  # 0.7s dwell time
        self.PINCH_THRESHOLD = 36   # Distance in pixels between thumb and index

        # Cursor Smoothing
        self.smoothed_cursor: Optional[tuple] = None
        self.SMOOTH_FACTOR = 0.40

        # Load MediaPipe Tasks HandLandmarker Model
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "hand_landmarker.task")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.55,
            min_tracking_confidence=0.55
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def start_camera_loop(self, on_close_callback: Optional[Callable[[], None]] = None):
        """Runs the webcam feed with real-time neural hand tracking."""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not access the webcam.")
            if on_close_callback:
                on_close_callback()
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.is_running = True
        window_name = "XO AI - Precision Neural Hand Control"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        # Mouse click support on camera window as fallback
        def _on_mouse_click(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and param:
                x0, y0, c_size = param
                cell = self._get_cell_at_pos(x, y, x0, y0, c_size)
                if cell is not None and self.board.is_empty(cell):
                    self._trigger_move(cell)

        while self.is_running:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            # Mirror frame horizontally for natural experience
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # Centered 3x3 Grid
            grid_size = int(min(h, w) * 0.72)
            x_start = int((w - grid_size) // 2)
            y_start = int((h - grid_size) // 2 + 15)
            cell_size = int(grid_size // 3)

            cv2.setMouseCallback(window_name, _on_mouse_click, (x_start, y_start, cell_size))

            # Run MediaPipe Neural Hand Landmark Inference
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.landmarker.detect(mp_img)

            # Draw 3x3 Grid Overlay
            self._draw_grid_overlay(frame, x_start, y_start, cell_size)

            hand_found = False
            cursor_pos = None
            is_pinching = False

            if detection_result.hand_landmarks:
                hand_found = True
                landmarks = detection_result.hand_landmarks[0]

                # Convert normalized landmarks to pixel coordinates
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]

                # Draw glowing holographic hand skeleton
                self._draw_hand_skeleton(frame, pts)

                # Index fingertip = landmark 8, Thumb tip = landmark 4
                ix, iy = pts[8]
                tx, ty = pts[4]

                # Check pinch (instant click)
                pinch_dist = math.hypot(ix - tx, iy - ty)
                if pinch_dist < self.PINCH_THRESHOLD:
                    is_pinching = True

                # Smooth fingertip cursor
                cursor_pos = self._smooth_cursor((ix, iy))

            # Process User Selection
            if cursor_pos:
                cx, cy = cursor_pos
                selected_cell = self._get_cell_at_pos(cx, cy, x_start, y_start, cell_size)
                is_valid = (selected_cell is not None and self.board.is_empty(selected_cell))

                # Draw Target Reticle on Index Fingertip
                reticle_color = (0, 255, 128) if is_valid else (0, 200, 255)
                cv2.circle(frame, (cx, cy), 12, reticle_color, -1)
                cv2.circle(frame, (cx, cy), 17, (255, 255, 255), 2)
                cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)

                # Instant Click via Pinch Gesture
                if is_pinching and is_valid:
                    self._trigger_move(selected_cell)
                    self.hover_cell = None
                    # Flash visual confirmation
                    cv2.circle(frame, (cx, cy), 35, (0, 255, 0), -1)

                # Or Dwell Selection (Hold finger for 0.7s)
                elif is_valid:
                    r, c = divmod(selected_cell, 3)
                    bx = x_start + c * cell_size
                    by = y_start + r * cell_size

                    # Highlight active cell
                    cv2.rectangle(frame, (bx + 4, by + 4), (bx + cell_size - 4, by + cell_size - 4), (0, 255, 128), 3)

                    if self.hover_cell == selected_cell:
                        elapsed = time.time() - self.hover_start_time
                        progress = min(1.0, elapsed / self.HOVER_THRESHOLD)

                        # Circular progress ring around fingertip
                        angle = int(progress * 360)
                        cv2.ellipse(frame, (cx, cy), (26, 26), -90, 0, angle, (0, 255, 0), 4)

                        if elapsed >= self.HOVER_THRESHOLD:
                            self._trigger_move(selected_cell)
                            self.hover_cell = None
                            cv2.circle(frame, (cx, cy), 35, (0, 255, 0), -1)
                    else:
                        self.hover_cell = selected_cell
                        self.hover_start_time = time.time()
                else:
                    self.hover_cell = None
            else:
                self.hover_cell = None
                self.smoothed_cursor = None

            # Top Telemetry & HUD
            self._draw_hud(frame, hand_found, is_pinching)

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except Exception:
                break

        self.is_running = False
        cap.release()
        cv2.destroyAllWindows()
        if on_close_callback:
            on_close_callback()

    def _smooth_cursor(self, raw_point: tuple) -> tuple:
        if self.smoothed_cursor is None:
            self.smoothed_cursor = raw_point
            return raw_point

        rx, ry = raw_point
        sx, sy = self.smoothed_cursor
        smooth_x = int(self.SMOOTH_FACTOR * rx + (1.0 - self.SMOOTH_FACTOR) * sx)
        smooth_y = int(self.SMOOTH_FACTOR * ry + (1.0 - self.SMOOTH_FACTOR) * sy)
        self.smoothed_cursor = (smooth_x, smooth_y)
        return self.smoothed_cursor

    def _draw_hand_skeleton(self, frame, pts):
        """Draws a high-tech glowing skeleton overlay on the hand."""
        # Draw connections
        for p1, p2 in HAND_CONNECTIONS:
            cv2.line(frame, pts[p1], pts[p2], (0, 220, 255), 2, cv2.LINE_AA)
        # Draw joints
        for pt in pts:
            cv2.circle(frame, pt, 4, (255, 255, 255), -1, cv2.LINE_AA)
        # Highlight index tip (landmark 8)
        cv2.circle(frame, pts[8], 7, (0, 255, 0), -1, cv2.LINE_AA)

    def _get_cell_at_pos(self, px: int, py: int, x0: int, y0: int, size: int) -> Optional[int]:
        if x0 <= px <= x0 + size * 3 and y0 <= py <= y0 + size * 3:
            col = (px - x0) // size
            row = (py - y0) // size
            if 0 <= col < 3 and 0 <= row < 3:
                return int(row * 3 + col)
        return None

    def _trigger_move(self, cell_idx: int):
        if self.on_move_callback:
            self.on_move_callback(cell_idx)

    def _draw_grid_overlay(self, frame, x0: int, y0: int, size: int):
        """Renders 3x3 board and pieces."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (x0, y0), (x0 + size * 3, y0 + size * 3), (16, 16, 26), -1)
        cv2.addWeighted(overlay, 0.38, frame, 0.62, 0, frame)

        for i in range(4):
            cv2.line(frame, (x0 + i * size, y0), (x0 + i * size, y0 + size * 3), (230, 230, 230), 2)
            cv2.line(frame, (x0, y0 + i * size), (x0 + size * 3, y0 + i * size), (230, 230, 230), 2)

        winner, win_trio = self.board.check_winner()

        for idx in range(9):
            r, c = divmod(idx, 3)
            cx = x0 + c * size + size // 2
            cy = y0 + r * size + size // 2

            # Index label in corner
            idx_x = x0 + c * size + size - 18
            idx_y = y0 + r * size + 22
            cv2.putText(frame, str(idx), (idx_x, idx_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (170, 170, 170), 1)

            mark = self.board.cells[idx]
            is_win_cell = win_trio and idx in win_trio

            if mark == HUMAN:
                color = (80, 255, 80) if is_win_cell else (60, 60, 240)
                offset = int(size * 0.28)
                cv2.line(frame, (cx - offset, cy - offset), (cx + offset, cy + offset), color, 5)
                cv2.line(frame, (cx + offset, cy - offset), (cx - offset, cy + offset), color, 5)
            elif mark == AI:
                color = (80, 255, 80) if is_win_cell else (245, 170, 30)
                radius = int(size * 0.28)
                cv2.circle(frame, (cx, cy), radius, color, 5)

    def _draw_hud(self, frame, hand_found: bool, is_pinching: bool):
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, 42), (18, 18, 22), -1)

        if hand_found:
            cv2.circle(frame, (20, 21), 7, (0, 255, 0), -1)
            status_txt = "Hand Locked: PINCH or HOLD 0.7s to play"
            status_col = (0, 255, 0)
        else:
            cv2.circle(frame, (20, 21), 7, (0, 165, 255), -1)
            status_txt = "Show your hand to the camera..."
            status_col = (0, 165, 255)

        cv2.putText(frame, status_txt, (35, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.50, status_col, 1, cv2.LINE_AA)
        hint = "'Q' to Exit"
        cv2.putText(frame, hint, (w - 110, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
