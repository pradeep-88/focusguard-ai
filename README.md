## FocusGuard AI — Real-Time Phone Usage Detection System

**FocusGuard AI** is a production-grade computer vision system that uses YOLOv8 to detect mobile phone usage in front of a webcam and trigger immediate alerts.  
It is designed as a practical, maintainable reference implementation that can be adapted to focus/productivity tools, compliance monitoring, or educational environments.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Overview

FocusGuard AI continuously monitors a webcam stream and raises an alert when a **person** and a **mobile phone** are detected in the same frame. The core goals of this project are:

- **Operational practicality**: Runs on a standard laptop CPU without requiring a dedicated GPU
- **Clear separation of concerns**: Detection, decision logic, monitoring loop, and utilities are cleanly isolated
- **Extensibility**: Easy to plug in alternative models, alert channels, or storage mechanisms
- **Portfolio readiness**: Code and structure are suitable to demonstrate real-world computer vision skills

---

## Key Features

| Feature | Description |
|---|---|
| **Real-time detection** | Streams webcam at up to 30 FPS (hardware-dependent) |
| **YOLOv8n inference** | Lightweight nano model optimised for CPU workloads |
| **Dual detection logic** | Alerts trigger only when both `person` and `cell phone` classes are present |
| **Audio alert** | 880 Hz warning tone via `pygame` to immediately notify the user |
| **Visual overlay** | Red bounding boxes and an overlay banner when phone usage is detected |
| **Evidence capture** | Timestamped PNG screenshots written to `evidence/` for later review |
| **Alert cooldown** | Configurable cooldown (default 5 seconds) to prevent alert spamming |
| **Session statistics** | Frames processed, alert count, and session duration summarised on exit |

---

## When To Use This Project

- **Personal productivity**: Detect and discourage phone usage while working or studying
- **Demonstrations and workshops**: Show a complete, understandable pipeline from webcam to model to alert
- **Baseline for further work**: Start from this implementation to add advanced analytics, dashboards, or cloud logging

This repository is intentionally kept focused and free of unnecessary abstractions so it can serve as a solid foundation for experimentation.

---

## Project Structure

```text
focusguard-ai/
│
├── app.py                  # Entry point — run this to start monitoring
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.py         # All tunable parameters
│
├── core/
│   ├── detector.py         # YOLOv8 model loading + inference orchestration
│   ├── logic.py            # Alert decision logic + cooldown handling
│   └── monitoring.py       # Webcam loop + drawing overlays and HUD
│
├── utils/
│   ├── audio_alert.py      # pygame-based sound alert management
│   ├── evidence_saver.py   # Screenshot creation with timestamped filenames
│   └── stats.py            # Session statistics tracking and reporting
│
├── assets/
│   └── alert.wav           # Warning sound (generated on setup, optional)
│
├── evidence/               # Auto-saved screenshots (git-ignored)
└── models/                 # Optional: pre-downloaded YOLO weights
```

---

## Quick Start

### 1. Clone and enter the repository

```bash
git clone https://github.com/<your-username>/focusguard-ai.git
cd focusguard-ai
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

On first run, Ultralytics will automatically download the YOLOv8n weights file (`yolov8n.pt`) if it is not already present.

### 4. Start monitoring

```bash
python app.py
```

Press `q` inside the video window to gracefully terminate the session and print the session statistics.

---

## Configuration

Runtime behaviour is configured via `config/settings.py`:

```python
CONFIDENCE_THRESHOLD = 0.5     # Detection confidence (0.0 – 1.0)
ALERT_COOLDOWN       = 5       # Seconds between alerts
SAVE_EVIDENCE        = True    # Save screenshots on alert
CAMERA_INDEX         = 0       # 0 = built-in webcam
MODEL_NAME           = "yolov8n.pt"
```

Typical adjustments:

- Increase `CONFIDENCE_THRESHOLD` if you see too many false positives
- Increase `ALERT_COOLDOWN` if alerts are firing too frequently for your use case
- Set `SAVE_EVIDENCE` to `False` if you only care about real-time alerts and not historical screenshots
- Change `CAMERA_INDEX` if you have multiple cameras attached

---

## High-Level Architecture

```text
Webcam (OpenCV)
     │
     ▼
Frame Capture
     │
     ▼
YOLOv8 Detector  ──→  detected: person, cell phone
     │
     ▼
Alert Logic  (person AND phone?)
     │
  ┌──┴──────────────┐
  ▼                 ▼
Audio Alert   Evidence Saver
(pygame)      (cv2.imwrite)
     │
     ▼
Session Stats
```

The architecture deliberately keeps responsibilities simple:

- `detector.py` focuses on model loading and inference
- `logic.py` encapsulates when and how an alert should fire
- `monitoring.py` coordinates the capture → inference → alert pipeline

---

## Dependencies

| Package | Purpose |
|---|---|
| `ultralytics` | YOLOv8 model loading and inference |
| `opencv-python` | Webcam capture, frame handling, and drawing overlays |
| `numpy` | Numerical operations on model outputs |
| `pygame` | Cross-platform audio playback for alerts |

Refer to `requirements.txt` for exact versions used in this project.

---

## Evidence Captures

When `SAVE_EVIDENCE` is enabled, screenshots are automatically stored under `evidence/` using timestamped filenames:

```text
evidence/
├── phone_usage_2026-03-10_14-32-15.png
└── phone_usage_2026-03-10_14-35-42.png
```

These captures are useful for:

- Reviewing when and how often distractions occurred
- Building small datasets for further experimentation or fine-tuning
- Auditing alert quality over time

---

## Sample Session Output

```text
========================================
   FocusGuard AI — Phone Usage Monitor
========================================

[Detector] Loading model: yolov8n.pt
[Monitor]  Camera 0 opened @ target 30 FPS.
[Monitor]  Press 'q' inside the video window to quit.

[Logic]    Phone usage detected — triggering alert.
[Evidence] Screenshot saved → evidence/phone_usage_2026-03-10_14-32-15.png

==========================================
        FocusGuard AI — Session Stats
==========================================
  Frames Processed : 1420
  Phone Alerts     : 3
  Session Duration : 2m 32s
==========================================
```

This output is intended to be self-explanatory and can be extended with additional metrics if needed.

---

## Performance Characteristics

Actual performance depends heavily on your hardware and camera, but typical behaviour is:

| Metric | Value |
|---|---|
| Target FPS | 30 |
| Typical CPU FPS | 15–25 (modern MacBook or Intel i5 and above) |
| Model size | ~6 MB (`yolov8n`) |
| RAM usage | ~300 MB |

For significantly higher throughput or lower latency, consider:

- Switching to a GPU-backed environment
- Reducing input frame size before inference
- Moving to a lighter model variant if available

---

## Development Notes

- The codebase favours readability and explicit control flow over premature optimisation
- Side effects (audio, file I/O, display) are isolated in utility modules where possible
- The structure is suitable for incremental improvements such as:
  - Adding alternative alert channels (desktop notifications, webhooks, etc.)
  - Logging events to disk or a remote service
  - Wrapping the core logic in a GUI or web interface

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it, subject to the terms of the license.

---

## Acknowledgements

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [COCO Dataset](https://cocodataset.org/) for pre-trained detection classes
