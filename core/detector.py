"""
core/detector.py
================
Handles YOLOv8 model loading and object inference.

Responsibilities:
  - Load the YOLOv8 model once at startup.
  - Run per-frame inference.
  - Return a structured result dict with person/phone detection flags
    plus the raw bounding-box list for overlay rendering.
"""

import logging
from typing import Any, Dict, List

from ultralytics import YOLO

from config.settings import (
    MODEL_NAME,
    CONFIDENCE_THRESHOLD,
    PERSON_CLASS_ID,
    PHONE_CLASS_ID,
)

logger = logging.getLogger(__name__)


class PhoneDetector:
    """
    Wraps a YOLOv8 model for real-time person + cell-phone detection.

    Usage
    -----
    detector = PhoneDetector()
    result   = detector.detect(frame)
    # result = {"person_detected": bool, "phone_detected": bool, "boxes": [...]}
    """

    def __init__(self, model_path: str | None = None) -> None:
        """
        Load the YOLOv8 model.

        Parameters
        ----------
        model_path : str, optional
            Path / name of the model weights.
            Defaults to MODEL_NAME from settings.
        """
        model_path = model_path or MODEL_NAME
        logger.info("Loading model: %s", model_path)
        try:
            self.model = YOLO(model_path)
            logger.info("Model loaded successfully.")
        except Exception as exc:
            logger.exception("Failed to load model: %s", exc)
            raise

        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.person_class_id = PERSON_CLASS_ID
        self.phone_class_id = PHONE_CLASS_ID

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame: Any) -> Dict[str, Any]:
        """
        Run YOLOv8 inference on a single BGR frame.

        Parameters
        ----------
        frame : numpy.ndarray
            BGR image (OpenCV format).

        Returns
        -------
        dict with keys:
            person_detected : bool
            phone_detected  : bool
            boxes           : list[dict]  — one entry per detection
                Each dict: { "class_id", "label", "confidence",
                              "x1", "y1", "x2", "y2" }
        """
        result: Dict[str, Any] = {
            "person_detected": False,
            "phone_detected": False,
            "boxes": [],
        }

        try:
            # Run inference (verbose=False suppresses per-frame console spam)
            predictions = self.model(frame, verbose=False)
        except Exception as exc:
            logger.error("Inference error: %s", exc)
            return result

        boxes: List[Dict[str, Any]] = []

        for pred in predictions:
            if pred.boxes is None:
                continue

            for box in pred.boxes:
                confidence = float(box.conf[0])
                if confidence < self.confidence_threshold:
                    continue

                class_id = int(box.cls[0])
                label = self.model.names.get(class_id, str(class_id))
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                box_dict = {
                    "class_id": class_id,
                    "label": label,
                    "confidence": confidence,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                }
                boxes.append(box_dict)

                if class_id == self.person_class_id:
                    result["person_detected"] = True
                elif class_id == self.phone_class_id:
                    result["phone_detected"] = True

        result["boxes"] = boxes
        return result
