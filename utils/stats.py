"""
utils/stats.py
==============
Tracks and reports session statistics.

Responsibilities:
  - Record total frames processed.
  - Count phone-usage alert triggers.
  - Measure session duration.
  - Print a formatted summary to console.
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class SessionStats:
    """
    Lightweight in-memory statistics tracker for a monitoring session.

    Usage
    -----
    stats = SessionStats()
    stats.start_session()

    # Inside the loop:
    stats.record_frame()
    stats.record_alert()   # on each alert trigger

    # At session end:
    stats.end_session()
    stats.print_summary()
    """

    def __init__(self) -> None:
        self._frames_processed = 0
        self._phone_alerts = 0
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_session(self) -> None:
        """Mark the beginning of a monitoring session."""
        self._start_time = time.time()
        self._end_time = None
        self._frames_processed = 0
        self._phone_alerts = 0
        logger.info("Session started.")

    def end_session(self) -> None:
        """Mark the end of a monitoring session."""
        self._end_time = time.time()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_frame(self) -> None:
        """Increment the processed-frame counter by one."""
        self._frames_processed += 1

    def record_alert(self) -> None:
        """Increment the phone-alert counter by one."""
        self._phone_alerts += 1

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def frames_processed(self) -> int:
        return self._frames_processed

    @property
    def phone_alerts(self) -> int:
        return self._phone_alerts

    @property
    def session_duration_seconds(self) -> float:
        if self._start_time is None:
            return 0.0
        end = self._end_time if self._end_time else time.time()
        return end - self._start_time

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def print_summary(self) -> None:
        """Print a formatted session summary to stdout."""
        duration = self.session_duration_seconds
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_str = f"{minutes}m {seconds}s"

        logger.info("==========================================")
        logger.info("        FocusGuard AI — Session Stats")
        logger.info("==========================================")
        logger.info("  Frames Processed : %s", self._frames_processed)
        logger.info("  Phone Alerts     : %s", self._phone_alerts)
        logger.info("  Session Duration : %s", duration_str)
        logger.info("==========================================")
