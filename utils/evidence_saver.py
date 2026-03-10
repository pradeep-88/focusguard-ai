"""
utils/evidence_saver.py
=======================
Saves screenshot evidence when phone usage is detected.

Responsibilities:
  - Generate a timestamped filename.
  - Write the frame to the evidence/ directory using cv2.imwrite().
  - Log the save path to the console.
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional

import cv2

from config.settings import SAVE_EVIDENCE, EVIDENCE_FOLDER, EVIDENCE_FILENAME_PREFIX

logger = logging.getLogger(__name__)


class EvidenceSaver:
    """
    Captures and stores annotated screenshots of phone-usage events.

    Usage
    -----
    saver = EvidenceSaver()
    saver.save(frame)
    """

    def __init__(self) -> None:
        self.enabled = SAVE_EVIDENCE
        self.folder = EVIDENCE_FOLDER
        self.prefix = EVIDENCE_FILENAME_PREFIX

        if self.enabled:
            os.makedirs(self.folder, exist_ok=True)
            logger.info("Evidence folder ready: %s", os.path.abspath(self.folder))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, frame: Any) -> Optional[str]:
        """
        Save the given frame as a PNG screenshot with a timestamp filename.

        Parameters
        ----------
        frame : numpy.ndarray
            BGR image to save.

        Returns
        -------
        str | None
            Full path of the saved file, or None if saving is disabled / fails.
        """
        if not self.enabled:
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.prefix}_{timestamp}.png"
        filepath = os.path.join(self.folder, filename)

        try:
            success = cv2.imwrite(filepath, frame)
            if success:
                logger.info("Screenshot saved → %s", filepath)
                return filepath

            logger.error("cv2.imwrite failed for: %s", filepath)
        except Exception as exc:
            logger.error("Exception while saving: %s", exc)

        return None
