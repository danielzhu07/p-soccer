"""App configuration."""
import os
from pathlib import Path

# Base paths (project root = parent of backend)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_DIR = Path(os.environ.get("JOBS_DIR", PROJECT_ROOT / "data" / "jobs"))
JOBS_DIR.mkdir(parents=True, exist_ok=True)

# Model: use fine-tuned soccer model if present, else pretrained YOLOv8n
MODEL_PATH = os.environ.get("MODEL_PATH", "yolov8n.pt")
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "soccer_yolov8" / "best.pt"
if DEFAULT_MODEL_PATH.exists():
    MODEL_PATH = str(DEFAULT_MODEL_PATH)
