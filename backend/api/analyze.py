"""Upload, preview, and analyze recorded video sources."""
from datetime import datetime, timedelta
from pathlib import Path
import json
import re
import shutil
import subprocess
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from services.video_processor import analyze_mp4

router = APIRouter(prefix="/api", tags=["recorded video"])
BACKEND_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BACKEND_DIR / "storage"
VIDEO_DIR = STORAGE_DIR / "videos"
PROCESSED_DIR = STORAGE_DIR / "processed"
SNAPSHOT_DIR = STORAGE_DIR / "snapshots"
PREVIEW_DIR = STORAGE_DIR / "previews"
ANALYSIS_DIR = STORAGE_DIR / "analysis"


def _source_path(camera: models.Camera) -> Path:
    source_path = Path(camera.source_uri or "")
    if not source_path.is_absolute():
        source_path = BACKEND_DIR / source_path
    return source_path


def _make_preview(source: Path, camera_id: int) -> Path:
    import cv2

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview = PREVIEW_DIR / f"camera_{camera_id}.jpg"
    capture = cv2.VideoCapture(str(source))
    ok, frame = capture.read()
    capture.release()
    if not ok:
        raise HTTPException(400, "The uploaded file is not a readable video")
    cv2.imwrite(str(preview), frame)
    return preview


@router.post("/videos")
def upload_video(
    file: UploadFile = File(...),
    name: str = Form("Recorded video"),
    location: str = Form("Uploaded MP4"),
    environment: str = Form("normal"),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "video.mp4").suffix.lower()
    if suffix != ".mp4":
        raise HTTPException(400, "Only MP4 video is supported")
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", Path(file.filename or "video").stem).strip("_") or "video"
    filename = f"{stem}_{uuid4().hex[:8]}.mp4"
    destination = VIDEO_DIR / filename
    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    camera = models.Camera(
        name=name.strip() or Path(file.filename or "Recorded video").stem,
        location=location.strip() or "Uploaded MP4",
        source="mp4",
        source_uri=f"storage/videos/{filename}",
        status="online",
        environment=environment if environment in {"normal", "low_light", "partial_occlusion"} else "normal",
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    try:
        _make_preview(destination, camera.id)
    except Exception:
        db.delete(camera)
        db.commit()
        destination.unlink(missing_ok=True)
        raise
    return {
        "id": camera.id,
        "name": camera.name,
        "location": camera.location,
        "filename": filename,
        "video_url": f"/media/videos/{filename}",
        "preview_url": f"/media/previews/camera_{camera.id}.jpg",
        "environment": camera.environment,
    }


@router.get("/cameras/{camera_id}/preview")
def camera_preview(camera_id: int, db: Session = Depends(get_db)):
    camera = db.get(models.Camera, camera_id)
    if not camera:
        raise HTTPException(404, "Video source not found")
    source = _source_path(camera)
    if not source.exists():
        raise HTTPException(404, "Video file not found")
    preview = PREVIEW_DIR / f"camera_{camera_id}.jpg"
    if not preview.exists():
        preview = _make_preview(source, camera_id)
    return FileResponse(preview, media_type="image/jpeg")


@router.get("/analysis-result")
def saved_analysis_result(camera_id: int = 1, db: Session = Depends(get_db)):
    """Return the latest persisted artifact so page refresh keeps analyzed output."""
    camera = db.get(models.Camera, camera_id)
    if not camera:
        raise HTTPException(404, "Video source not found")
    web_output = PROCESSED_DIR / f"camera_{camera_id}_analyzed_h264.mp4"
    if not web_output.exists():
        raise HTTPException(404, "This video has not been analyzed yet")

    summary_path = ANALYSIS_DIR / f"camera_{camera_id}.json"
    if summary_path.exists():
        try:
            return json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass

    events = (
        db.query(models.Event)
        .filter(models.Event.camera_id == camera_id)
        .order_by(models.Event.video_seconds.asc())
        .all()
    )
    track_ids = {event.track_id for event in events if event.track_id is not None}
    return {
        "status": "completed",
        "camera_id": camera_id,
        "processed_video_url": f"/media/processed/{web_output.name}",
        "detector_engine": "Saved YOLOv8 + ByteTrack result",
        "risk_detector_engine": "Saved YOLOv8 firearm + COCO result",
        "processed_frames": 0,
        "unique_people": len(track_ids),
        "max_people_in_frame": len(track_ids),
        "restricted_zone_entries": sum(event.event_type == "restricted_zone" for event in events),
        "loitering_events": sum(event.event_type == "loitering" for event in events),
        "risk_object_events": sum(event.event_type == "risk_object" for event in events),
        "events": [
            {"id": event.id, "event_type": event.event_type}
            for event in events
        ],
    }


@router.post("/analyze-video")
def analyze_video(camera_id: int = 1, db: Session = Depends(get_db)):
    camera = db.get(models.Camera, camera_id)
    if not camera or not camera.source_uri:
        raise HTTPException(404, "Video source not found")
    source_path = _source_path(camera)
    if not source_path.exists():
        raise HTTPException(404, f"Video file not found: {source_path.name}")

    settings = db.query(models.SystemSettings).first()
    detection_threshold = settings.detection_threshold if settings else 0.5
    default_loitering = settings.loitering_threshold if settings else 30
    zones = [
        {
            "id": zone.id,
            "name": zone.name,
            "polygon": zone.polygon,
            "zone_type": zone.zone_type,
            "loitering_threshold": zone.loitering_threshold or default_loitering,
        }
        for zone in camera.zones
    ]
    raw_output = PROCESSED_DIR / f"camera_{camera_id}_analyzed.mp4"
    web_output = PROCESSED_DIR / f"camera_{camera_id}_analyzed_h264.mp4"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    try:
        summary = analyze_mp4(
            str(source_path), str(raw_output), zones,
            confidence=detection_threshold,
            snapshots_dir=str(SNAPSHOT_DIR), camera_id=camera_id,
        )
        from imageio_ffmpeg import get_ffmpeg_exe

        subprocess.run(
            [
                get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(raw_output),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(web_output),
            ], check=True,
        )
        raw_output.unlink(missing_ok=True)
    except ImportError as exc:
        raise HTTPException(503, "Video dependencies are not installed") from exc
    except Exception as exc:
        raise HTTPException(500, f"Video analysis failed: {exc}") from exc

    duration = (summary.get("total_frames") or 0) / (summary.get("fps") or 25)
    video_started_at = datetime.utcnow() - timedelta(seconds=duration)
    db.query(models.Event).filter(models.Event.camera_id == camera_id).delete()
    saved_events = []
    for candidate in summary.pop("events", []):
        event = models.Event(
            camera_id=camera_id,
            track_id=candidate.get("track_id"),
            event_type=candidate["event_type"],
            alert_level="ALERT" if candidate["event_type"] == "risk_object" else "WATCH",
            confidence=candidate.get("confidence"),
            snapshot=candidate.get("snapshot"),
            timestamp=video_started_at + timedelta(seconds=candidate.get("video_seconds", 0)),
            video_seconds=candidate.get("video_seconds"),
            response_time_ms=candidate.get("response_time_ms"),
            review_status="pending",
        )
        db.add(event)
        db.flush()
        saved_events.append({
            "id": event.id, "event_type": event.event_type,
            "track_id": event.track_id, "alert_level": event.alert_level,
            "snapshot": event.snapshot,
            "video_seconds": candidate.get("video_seconds", 0),
        })
    db.commit()

    response = {
        "status": "completed", "camera_id": camera_id,
        "source_video_url": f"/media/videos/{source_path.name}",
        "processed_video_url": f"/media/processed/{web_output.name}",
        "events": saved_events, **summary,
    }
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    (ANALYSIS_DIR / f"camera_{camera_id}.json").write_text(
        json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return response
