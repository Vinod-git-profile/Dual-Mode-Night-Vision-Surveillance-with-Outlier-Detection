"""
Configuration file for Night Vision Surveillance System
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"

# Ensure directories exist
UPLOADS_DIR.mkdir(exist_ok=True)
SNAPSHOTS_DIR.mkdir(exist_ok=True)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "night_vision_surveillance")

# YOLO Configuration
YOLO_MODEL = "yolov8n.pt"  # Nano model for speed
YOLO_CONF_THRESHOLD = 0.45
YOLO_IOU_THRESHOLD = 0.5

# COCO class IDs
PERSON_CLASS_ID = 0
ANIMAL_CLASS_IDS = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23]  # bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
VEHICLE_CLASS_IDS = [1, 2, 3, 5, 7]  # bicycle, car, motorcycle, bus, truck

# Processing Configuration
UI_FPS = 20  # Display frame rate
AI_FPS = 10  # Analytics processing rate
MAX_TRACK_AGE = 50  # frames
MAX_TRACK_DISTANCE = 100  # pixels

# Enhancement Configuration
LOW_LIGHT_THRESHOLD = 80  # Average brightness below this triggers enhancement
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Anomaly Detection Configuration - HUMAN MODE
LOITER_SECONDS = 300  # 5 minutes
CROWD_THRESHOLD = 5  # Number of people

# Anomaly Detection Configuration - ANIMAL MODE
ANIMAL_SPIKE_THRESHOLD = 3  # Count increase
SPIKE_WINDOW_SECONDS = 60  # Time window for spike detection
ANIMAL_BASELINE_SMOOTHING = 0.99  # Exponential moving average

# Severity Levels
SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"

# Stream Configuration
STREAM_QUALITY = 85  # JPEG quality
STREAM_MAX_WIDTH = 1280

# Camera Configuration
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30
