"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ModeEnum(str, Enum):
    HUMAN = "human"
    ANIMAL = "animal"

class SourceTypeEnum(str, Enum):
    CAMERA = "camera"
    FILE = "file"

class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class LogLevelEnum(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"

# Request Models
class SourceRequest(BaseModel):
    type: SourceTypeEnum
    value: Any  # int for camera, str for file path

class AnalyticsRequest(BaseModel):
    enabled: bool

class ModeRequest(BaseModel):
    mode: ModeEnum

# Response Models
class CameraDevice(BaseModel):
    index: int
    name: str
    available: bool

class Detection(BaseModel):
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float
    class_id: int
    class_name: str
    category: str  # person, animal, vehicle
    track_id: Optional[int] = None

class VideoState(BaseModel):
    source_type: Optional[str] = None
    source_value: Optional[Any] = None
    mode: str
    analytics_enabled: bool
    cuda_available: bool
    is_running: bool
    person_count: int
    animal_count: int
    vehicle_count: int
    last_event: Optional[str] = None
    last_event_time: Optional[str] = None

class Event(BaseModel):
    event_id: str
    camera_id: str
    mode: str
    event_type: str
    severity: str
    description: str
    snapshot_path: Optional[str] = None
    metadata: Dict[str, Any]
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Log(BaseModel):
    log_id: str
    camera_id: str
    level: str
    message: str
    metadata: Dict[str, Any]
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EventsResponse(BaseModel):
    events: List[Event]
    total: int

class LogsResponse(BaseModel):
    logs: List[Log]
    total: int
