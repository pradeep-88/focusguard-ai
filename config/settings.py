# ============================================================
# FocusGuard AI — Configuration Settings
# ============================================================
# All tunable parameters are defined here for easy adjustment
# without modifying core logic.

# --- Camera Settings ---
CAMERA_INDEX = 0  # 0 = default webcam; change for external cameras

# --- Model Settings ---
MODEL_NAME = "yolov8n.pt"  # YOLOv8 nano model (fastest for CPU inference)

# --- Detection Profiles ---
# Profiles allow quick switching between conservative, balanced, and aggressive
# detection behaviour.
DETECTION_PROFILES = {
    "conservative": {
        "confidence_threshold": 0.6,
        "alert_cooldown": 8,
    },
    "balanced": {
        "confidence_threshold": 0.5,
        "alert_cooldown": 5,
    },
    "aggressive": {
        "confidence_threshold": 0.4,
        "alert_cooldown": 3,
    },
}

# Active profile key from DETECTION_PROFILES.
ACTIVE_DETECTION_PROFILE = "balanced"

profile = DETECTION_PROFILES[ACTIVE_DETECTION_PROFILE]

# --- Detection Settings ---
CONFIDENCE_THRESHOLD = profile["confidence_threshold"]  # Minimum confidence (0.0 – 1.0)

# COCO class IDs used by YOLOv8
PERSON_CLASS_ID = 0  # COCO class: person
PHONE_CLASS_ID = 67  # COCO class: cell phone

# --- Alert Settings ---
ALERT_COOLDOWN = profile["alert_cooldown"]  # Seconds between consecutive alerts
ALERT_SOUND_PATH = "assets/alert.wav"  # Path to the warning sound file

# --- Evidence Settings ---
SAVE_EVIDENCE = False  # Enable/disable screenshot capture on alert
EVIDENCE_FOLDER = "evidence"  # Folder where screenshots are stored
EVIDENCE_FILENAME_PREFIX = "phone_usage"

# --- Display Settings ---
WINDOW_NAME = "FocusGuard AI — Monitor"
FONT_SCALE = 0.7
FONT_THICKNESS = 2
COLOR_NORMAL = (0, 255, 0)  # Green — normal bounding box
COLOR_ALERT = (0, 0, 255)  # Red   — phone usage detected
COLOR_TEXT = (255, 255, 255)  # White — overlay text

# --- Performance Settings ---
TARGET_FPS = 30  # Desired capture frame rate (actual inference may be lower on CPU)
