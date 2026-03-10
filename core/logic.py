"""
core/logic.py
=============
Decision logic for phone-usage detection.

Responsibilities:
  - Determine whether an alert should be triggered based on
    the detection result from the YOLOv8 detector.
  - Enforce the cooldown period between consecutive alerts.
  - Coordinate downstream actions (audio alert, evidence saving).
"""

import logging
import time
from typing import Any, Callable, Dict

from config.settings import ALERT_COOLDOWN

logger = logging.getLogger(__name__)


class AlertLogic:
    """
    Stateful decision engine that enforces alert cooldown and
    dispatches alert actions when phone usage is detected.

    Parameters
    ----------
    audio_alert   : callable  — play the warning sound
    evidence_saver: callable  — save a screenshot, receives the frame
    stats_tracker : object    — has .record_alert() method
    """

    def __init__(
        self,
        audio_alert: Callable[[], None],
        evidence_saver: Callable[[Any], Any],
        stats_tracker: Any,
    ) -> None:
        self.audio_alert = audio_alert
        self.evidence_saver = evidence_saver
        self.stats_tracker = stats_tracker

        self.cooldown_seconds = ALERT_COOLDOWN
        self._last_alert_time = 0.0  # epoch timestamp of last triggered alert
        self.alert_active = False  # True during a cooldown window

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, detection_result: Dict[str, Any], frame: Any) -> bool:
        """
        Evaluate the detection result and trigger alerts if warranted.

        Parameters
        ----------
        detection_result : dict
            Output of PhoneDetector.detect(): contains
            'person_detected', 'phone_detected', 'boxes'.
        frame : numpy.ndarray
            Current BGR frame (needed for evidence saving).

        Returns
        -------
        bool
            True  → phone usage detected (alert is/was triggered)
            False → no phone usage
        """
        person_detected = detection_result.get("person_detected", False)
        phone_detected = detection_result.get("phone_detected", False)

        if not (person_detected and phone_detected):
            # No phone usage; clear active-alert flag
            self.alert_active = False
            return False

        # Phone usage confirmed — check cooldown
        now = time.time()
        if now - self._last_alert_time >= self.cooldown_seconds:
            self._trigger_alert(frame)
            self._last_alert_time = now

        # Keep alert_active True throughout the cooldown window
        self.alert_active = True
        return True

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _trigger_alert(self, frame: Any) -> None:
        """Fire all alert actions once per cooldown window."""
        logger.warning("⚠  Phone usage detected — triggering alert.")

        # 1. Play warning sound
        try:
            self.audio_alert()
        except Exception as exc:
            logger.error("Audio alert failed: %s", exc)

        # 2. Save screenshot evidence
        try:
            self.evidence_saver(frame)
        except Exception as exc:
            logger.error("Evidence save failed: %s", exc)

        # 3. Update statistics
        try:
            self.stats_tracker.record_alert()
        except Exception as exc:
            logger.error("Stats update failed: %s", exc)
