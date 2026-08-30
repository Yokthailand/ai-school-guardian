from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CameraIn(BaseModel):
    name: str
    location: Optional[str] = None
    source: str          # mp4 | webcam | rtsp
    source_uri: Optional[str] = None
    environment: str = "normal"


class CameraOut(CameraIn):
    id: int
    status: str

    class Config:
        from_attributes = True


class ZoneIn(BaseModel):
    camera_id: int
    name: str
    polygon: List[List[float]]   # normalized coordinates
    zone_type: str = "restricted"
    loitering_threshold: int = 30


class ZoneOut(ZoneIn):
    id: int

    class Config:
        from_attributes = True


class EventOut(BaseModel):
    id: int
    camera_id: int
    track_id: Optional[int]
    event_type: str
    alert_level: str
    confidence: Optional[float]
    snapshot: Optional[str]
    timestamp: datetime
    video_seconds: Optional[float] = None
    response_time_ms: Optional[float] = None
    review_status: str = "pending"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatisticsOut(BaseModel):
    alerts_today: int
    restricted_zone_count: int
    loitering_count: int
    risk_object_count: int
    cameras_online: int
    cameras_total: int
    watch_count: int = 0
    alert_count: int = 0
    pending_review_count: int = 0


class GroundTruthIn(BaseModel):
    camera_id: int
    event_type: str
    video_seconds: float
    tolerance_seconds: float = 2.0
    description: Optional[str] = None


class GroundTruthOut(GroundTruthIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventReviewIn(BaseModel):
    status: str
    reviewed_by: str


class SettingsIn(BaseModel):
    detection_threshold: float = 0.5
    loitering_threshold: int = 30
    alert_settings: dict = {}


class SettingsOut(SettingsIn):
    id: int

    class Config:
        from_attributes = True
