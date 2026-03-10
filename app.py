"""
app.py
======
FocusGuard AI — Entry Point

Run this file to start the real-time phone usage detection monitor:

    python app.py

The script wires up all modules and launches the webcam loop.
"""

import logging
import os
import sys
from typing import NoReturn

from core.detector import PhoneDetector
from core.logic import AlertLogic
from core.monitoring import Monitor
from utils.audio_alert import AudioAlert
from utils.evidence_saver import EvidenceSaver
from utils.stats import SessionStats


def configure_logging() -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> None:
    """Application entrypoint."""
    configure_logging()
    logger = logging.getLogger(__name__)

    logger.info("========================================")
    logger.info("   FocusGuard AI — Phone Usage Monitor")
    logger.info("========================================")

    # --- Instantiate utility components ---
    stats = SessionStats()
    audio = AudioAlert()
    saver = EvidenceSaver()

    # --- Instantiate core components ---
    detector = PhoneDetector()
    logic = AlertLogic(
        audio_alert=audio.play,
        evidence_saver=saver.save,
        stats_tracker=stats,
    )
    monitor = Monitor(
        detector=detector,
        alert_logic=logic,
        stats_tracker=stats,
    )

    # --- Start monitoring ---
    monitor.start()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.getLogger(__name__).exception("[App] Fatal error: %s", exc)
        sys.exit(1)
