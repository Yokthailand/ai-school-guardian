from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas import SettingsIn, SettingsOut

router = APIRouter(prefix="/api/settings", tags=["settings"])


def get_or_create(db: Session) -> models.SystemSettings:
    settings = db.query(models.SystemSettings).first()
    if settings is None:
        settings = models.SystemSettings(
            detection_threshold=0.5,
            loitering_threshold=30,
            alert_settings={"human_verification_required": True},
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("", response_model=SettingsOut)
def read_settings(db: Session = Depends(get_db)):
    return get_or_create(db)


@router.put("", response_model=SettingsOut)
def update_settings(payload: SettingsIn, db: Session = Depends(get_db)):
    settings = get_or_create(db)
    settings.detection_threshold = min(1.0, max(0.05, payload.detection_threshold))
    settings.loitering_threshold = max(1, payload.loitering_threshold)
    settings.alert_settings = {
        **(payload.alert_settings or {}),
        "human_verification_required": True,
    }
    db.commit()
    db.refresh(settings)
    return settings
