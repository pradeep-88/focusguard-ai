"""
core/monitoring.py
==================
Main webcam loop, frame processing, and visual overlay rendering.

Responsibilities:
  - Open and manage the webcam stream.
  - Drive the per-frame detection + alert pipeline.
  - Render bounding boxes, labels, and alert banner on each frame.
  - Expose a clean start() method used by app.py.
"""

import logging
from typing import Any, Dict

import cv2
import time

from config.settings import (
    CAMERA_INDEX,
    WINDOW_NAME,
    TARGET_FPS,
    COLOR_NORMAL,
    COLOR_ALERT,
    COLOR_TEXT,
    FONT_SCALE,
    FONT_THICKNESS,
)

logger = logging.getLogger(__name__)


class Monitor:
    """
    Orchestrates the real-time webcam monitoring loop.

    Parameters
    ----------
    detector      : PhoneDetector  — runs YOLOv8 inference
    alert_logic   : AlertLogic     — decides when to trigger alerts
    stats_tracker : SessionStats   — records frame counts / durations
    """

    def __init__(self, detector: Any, alert_logic: Any, stats_tracker: Any) -> None:
        self.detector = detector
        self.alert_logic = alert_logic
        self.stats_tracker = stats_tracker

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Open the webcam and run the monitoring loop until 'q' is pressed."""
        cap = self._open_camera()
        if cap is None:
            return

        logger.info("Press 'q' inside the video window to quit.")
        self.stats_tracker.start_session()

        try:
            self._run_loop(cap)
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user.")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.stats_tracker.end_session()
            self.stats_tracker.print_summary()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _open_camera(self):
        """Try to open the webcam; return None on failure."""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            logger.error("Cannot open camera index %s.", CAMERA_INDEX)
            return None

        cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
        logger.info("Camera %s opened @ target %s FPS.", CAMERA_INDEX, TARGET_FPS)
        return cap

    def _run_loop(self, cap) -> None:
        """Core frame-processing loop."""
        frame_delay = 1.0 / TARGET_FPS  # minimum seconds between frames

        while True:
            loop_start = time.time()

            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame; retrying…")
                time.sleep(0.05)
                continue

            # --- Detection ---
            detection_result = self.detector.detect(frame)

            # --- Alert evaluation ---
            alert_active = self.alert_logic.evaluate(detection_result, frame)

            # --- Update stats ---
            self.stats_tracker.record_frame()

            # --- Render overlay ---
            annotated = self._draw_overlay(frame, detection_result, alert_active)

            # --- Display ---
            cv2.imshow(WINDOW_NAME, annotated)

            # --- Quit on 'q' ---
            if cv2.waitKey(1) & 0xFF == ord("q"):
                logger.info("Quit key pressed.")
                break

            # --- Throttle to target FPS ---
            elapsed = time.time() - loop_start
            sleep_time = frame_delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _draw_overlay(
        self,
        frame: Any,
        detection_result: Dict[str, Any],
        alert_active: bool,
    ) -> Any:
        """Draw bounding boxes, labels, and optional alert banner."""
        annotated = frame.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Choose colour scheme based on alert state
        box_color = COLOR_ALERT if alert_active else COLOR_NORMAL

        # --- Draw bounding boxes ---
        for box in detection_result.get("boxes", []):
            x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]
            label = f"{box['label']} {box['confidence']:.2f}"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)

            # Label background for readability
            (tw, th), _ = cv2.getTextSize(label, font, FONT_SCALE, FONT_THICKNESS)
            cv2.rectangle(
                annotated,
                (x1, y1 - th - 8),
                (x1 + tw + 4, y1),
                box_color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 2, y1 - 4),
                font,
                FONT_SCALE,
                COLOR_TEXT,
                FONT_THICKNESS,
                lineType=cv2.LINE_AA,
            )

        # --- Alert banner ---
        if alert_active:
            self._draw_alert_banner(annotated, font)

        # --- Status line (bottom-left) ---
        self._draw_status_line(annotated, font)

        return annotated

    def _draw_alert_banner(self, frame: Any, font: Any) -> None:
        """Render a prominent red banner at the top of the frame."""
        banner_text = "  WARNING: PHONE USAGE DETECTED  "
        (tw, th), _ = cv2.getTextSize(banner_text, font, 0.9, 2)
        h, w = frame.shape[:2]

        # Semi-transparent red rectangle
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, th + 24), (0, 0, 200), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Centred warning text
        x_pos = max(0, (w - tw) // 2)
        cv2.putText(
            frame,
            banner_text,
            (x_pos, th + 10),
            font,
            0.9,
            (255, 255, 255),
            2,
            lineType=cv2.LINE_AA,
        )

    def _draw_status_line(self, frame: Any, font: Any) -> None:
        """Render a small status line at the bottom of the frame."""
        h, w = frame.shape[:2]
        status = "FocusGuard AI  |  Press 'q' to quit"
        cv2.putText(
            frame,
            status,
            (8, h - 10),
            font,
            0.5,
            (200, 200, 200),
            1,
            lineType=cv2.LINE_AA,
        )
