from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database.database import get_db
from database import models
from schemas import EventOut, EventReviewIn

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[EventOut])
def list_events(
    db: Session = Depends(get_db),
    camera_id: Optional[int] = None,
    event_type: Optional[str] = None,
    alert_level: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    review_status: Optional[str] = None,
    limit: int = 100,
):
    q = db.query(models.Event)
    if camera_id is not None:
        q = q.filter(models.Event.camera_id == camera_id)
    if event_type is not None:
        q = q.filter(models.Event.event_type == event_type)
    if alert_level is not None:
        q = q.filter(models.Event.alert_level == alert_level)
    if date_from is not None:
        q = q.filter(models.Event.timestamp >= date_from)
    if date_to is not None:
        q = q.filter(models.Event.timestamp <= date_to)
    if review_status is not None:
        q = q.filter(models.Event.review_status == review_status)
    return q.order_by(models.Event.timestamp.desc()).limit(limit).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.query(models.Event).get(event_id)
    if not ev:
        raise HTTPException(404, "Event not found")
    return ev


@router.patch("/{event_id}/review", response_model=EventOut)
def review_event(event_id: int, payload: EventReviewIn, db: Session = Depends(get_db)):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(404, "Event not found")
    if payload.status not in {"pending", "confirmed", "rejected"}:
        raise HTTPException(400, "Status must be pending, confirmed, or rejected")
    ev.review_status = payload.status
    ev.reviewed_by = payload.reviewed_by.strip() or "Authorized staff"
    ev.reviewed_at = datetime.utcnow() if payload.status != "pending" else None
    db.commit()
    db.refresh(ev)
    return ev
