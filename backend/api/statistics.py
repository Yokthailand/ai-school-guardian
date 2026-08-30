from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database.database import get_db
from database import models
from schemas import StatisticsOut

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("", response_model=StatisticsOut)
def get_statistics(db: Session = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    def count_today(event_type: str | None = None):
        q = db.query(func.count(models.Event.id)).filter(
            models.Event.timestamp >= today_start
        )
        if event_type:
            q = q.filter(models.Event.event_type == event_type)
        return q.scalar() or 0

    cameras_total = db.query(func.count(models.Camera.id)).scalar() or 0
    cameras_online = (
        db.query(func.count(models.Camera.id))
        .filter(models.Camera.status == "online")
        .scalar()
        or 0
    )

    return StatisticsOut(
        alerts_today=count_today(),
        restricted_zone_count=count_today("restricted_zone"),
        loitering_count=count_today("loitering"),
        risk_object_count=count_today("risk_object"),
        cameras_online=cameras_online,
        cameras_total=cameras_total,
        watch_count=db.query(func.count(models.Event.id)).filter(
            models.Event.timestamp >= today_start, models.Event.alert_level == "WATCH"
        ).scalar() or 0,
        alert_count=db.query(func.count(models.Event.id)).filter(
            models.Event.timestamp >= today_start, models.Event.alert_level == "ALERT"
        ).scalar() or 0,
        pending_review_count=db.query(func.count(models.Event.id)).filter(
            models.Event.review_status == "pending"
        ).scalar() or 0,
    )
