"""
Step 9 — Event Engine.

Turns raw detections (restricted_zone / loitering / risk_object) into
Event rows with an alert_level, then hands off to the WebSocket
broadcaster (Step 10) for the live dashboard.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from database import models

ALERT_LEVELS = {
    "restricted_zone": "WATCH",
    "loitering": "WATCH",
    "risk_object": "ALERT",
}


def raise_event(
    db: Session,
    camera_id: int,
    event_type: str,
    track_id: int | None = None,
    confidence: float | None = None,
    snapshot: str | None = None,
) -> models.Event:
    event = models.Event(
        camera_id=camera_id,
        track_id=track_id,
        event_type=event_type,
        alert_level=ALERT_LEVELS.get(event_type, "WATCH"),
        confidence=confidence,
        snapshot=snapshot,
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Step 10: broadcast over WebSocket to connected dashboards
    from api.ws import broadcast_event  # local import avoids circular import
    broadcast_event(event)

    return event
