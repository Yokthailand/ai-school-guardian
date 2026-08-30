from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    source = Column(String, nullable=False)   # "mp4" | "webcam" | "rtsp"
    source_uri = Column(String, nullable=True)  # file path / device index / rtsp url
    status = Column(String, default="offline")  # "online" | "offline"
    environment = Column(String, default="normal")  # normal | low_light | partial_occlusion

    zones = relationship("Zone", back_populates="camera")
    events = relationship("Event", back_populates="camera")


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    name = Column(String, nullable=False)
    polygon = Column(JSON, nullable=False)     # normalized [[x,y], ...]
    zone_type = Column(String, default="restricted")  # "restricted" | "loitering"
    loitering_threshold = Column(Integer, default=30)  # seconds

    camera = relationship("Camera", back_populates="zones")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    track_id = Column(Integer, nullable=True)
    event_type = Column(String, nullable=False)   # "restricted_zone" | "loitering" | "risk_object"
    alert_level = Column(String, nullable=False)  # "NORMAL" | "WATCH" | "ALERT"
    confidence = Column(Float, nullable=True)
    snapshot = Column(String, nullable=True)      # path under storage/snapshots
    timestamp = Column(DateTime, default=datetime.utcnow)
    video_seconds = Column(Float, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    review_status = Column(String, default="pending")  # pending | confirmed | rejected
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    camera = relationship("Camera", back_populates="events")


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    detection_threshold = Column(Float, default=0.5)
    loitering_threshold = Column(Integer, default=30)
    alert_settings = Column(JSON, default=dict)


class GroundTruth(Base):
    __tablename__ = "ground_truth"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    event_type = Column(String, nullable=False)  # restricted_zone | loitering | risk_object | normal
    video_seconds = Column(Float, nullable=False)
    tolerance_seconds = Column(Float, default=2.0)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
