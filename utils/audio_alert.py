"""
utils/audio_alert.py
====================
Manages warning sound alerts using pygame.mixer.

Responsibilities:
  - Initialise pygame audio at startup.
  - Load the alert WAV file once.
  - Provide a simple play() function called by the alert logic.
"""

import logging
import os
from typing import Optional

import pygame

from config.settings import ALERT_SOUND_PATH

logger = logging.getLogger(__name__)


class AudioAlert:
    """
    Wraps pygame.mixer for non-blocking sound playback.

    Usage
    -----
    audio = AudioAlert()
    audio.play()          # play warning sound
    """

    def __init__(self, sound_path: Optional[str] = None) -> None:
        """
        Initialise pygame mixer and load the alert sound.

        Parameters
        ----------
        sound_path : str, optional
            Override for the default ALERT_SOUND_PATH setting.
        """
        self.sound_path = sound_path or ALERT_SOUND_PATH
        self._sound: Optional[pygame.mixer.Sound] = None
        self._available = False

        self._init_mixer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def play(self) -> None:
        """Play the alert sound (non-blocking). Fails silently if unavailable."""
        if not self._available or self._sound is None:
            return
        try:
            self._sound.play()
        except Exception as exc:
            logger.error("Playback error: %s", exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _init_mixer(self) -> None:
        """Try to initialise pygame.mixer and load the WAV file."""
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        except Exception as exc:
            logger.warning("pygame.mixer init failed (no audio?): %s", exc)
            return

        if not os.path.exists(self.sound_path):
            logger.warning(
                "Sound file not found: %s. Alert sound will be silent.",
                self.sound_path,
            )
            return

        try:
            self._sound = pygame.mixer.Sound(self.sound_path)
            self._available = True
            logger.info("Sound loaded: %s", self.sound_path)
        except Exception as exc:
            logger.error("Failed to load sound: %s", exc)
