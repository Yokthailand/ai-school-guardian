from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas import CameraIn, CameraOut

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


@router.get("", response_model=list[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(models.Camera).all()


@router.post("", response_model=CameraOut)
def create_camera(camera: CameraIn, db: Session = Depends(get_db)):
    db_camera = models.Camera(**camera.model_dump(), status="offline")
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.put("/{camera_id}", response_model=CameraOut)
def update_camera(camera_id: int, camera: CameraIn, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).get(camera_id)
    if not db_camera:
        raise HTTPException(404, "Camera not found")
    for k, v in camera.model_dump().items():
        setattr(db_camera, k, v)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.get(models.Camera, camera_id)
    if not db_camera:
        raise HTTPException(404, "Camera not found")
    backend_dir = Path(__file__).resolve().parents[1]
    source_path = Path(db_camera.source_uri or "")
    if not source_path.is_absolute():
        source_path = backend_dir / source_path
    db.query(models.Event).filter(models.Event.camera_id == camera_id).delete()
    db.query(models.Zone).filter(models.Zone.camera_id == camera_id).delete()
    db.query(models.GroundTruth).filter(models.GroundTruth.camera_id == camera_id).delete()
    db.delete(db_camera)
    db.commit()
    storage = (backend_dir / "storage").resolve()
    try:
        resolved_source = source_path.resolve()
        if storage in resolved_source.parents:
            resolved_source.unlink(missing_ok=True)
    except OSError:
        pass
    for artifact in [
        backend_dir / "storage" / "previews" / f"camera_{camera_id}.jpg",
        backend_dir / "storage" / "processed" / f"camera_{camera_id}_analyzed.mp4",
        backend_dir / "storage" / "processed" / f"camera_{camera_id}_analyzed_h264.mp4",
        backend_dir / "storage" / "analysis" / f"camera_{camera_id}.json",
    ]:
        artifact.unlink(missing_ok=True)
    for snapshot in (backend_dir / "storage" / "snapshots").glob(f"camera_{camera_id}_*.jpg"):
        snapshot.unlink(missing_ok=True)
    return {"deleted": camera_id}
