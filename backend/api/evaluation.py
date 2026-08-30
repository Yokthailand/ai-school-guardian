"""Ground-truth authoring and reproducible evaluation for recorded videos."""
from io import StringIO
import csv

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas import GroundTruthIn, GroundTruthOut

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])
VALID_TYPES = {"normal", "restricted_zone", "loitering", "risk_object"}


@router.get("/ground-truth", response_model=list[GroundTruthOut])
def list_ground_truth(camera_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.GroundTruth)
    if camera_id is not None:
        query = query.filter(models.GroundTruth.camera_id == camera_id)
    return query.order_by(models.GroundTruth.video_seconds).all()


@router.post("/ground-truth", response_model=GroundTruthOut)
def create_ground_truth(payload: GroundTruthIn, db: Session = Depends(get_db)):
    if payload.event_type not in VALID_TYPES:
        raise HTTPException(400, "Invalid ground-truth event type")
    if not db.get(models.Camera, payload.camera_id):
        raise HTTPException(404, "Video source not found")
    truth = models.GroundTruth(**payload.model_dump())
    db.add(truth)
    db.commit()
    db.refresh(truth)
    return truth


@router.delete("/ground-truth/{truth_id}")
def delete_ground_truth(truth_id: int, db: Session = Depends(get_db)):
    truth = db.get(models.GroundTruth, truth_id)
    if not truth:
        raise HTTPException(404, "Ground truth not found")
    db.delete(truth)
    db.commit()
    return {"deleted": truth_id}


def calculate(camera_id: int, db: Session) -> dict:
    camera = db.get(models.Camera, camera_id)
    if not camera:
        raise HTTPException(404, "Video source not found")
    truths = db.query(models.GroundTruth).filter(models.GroundTruth.camera_id == camera_id).all()
    events = db.query(models.Event).filter(models.Event.camera_id == camera_id).all()
    if not truths:
        response_values = [event.response_time_ms for event in events if event.response_time_ms is not None]
        return {
            "camera_id": camera_id, "video_name": camera.name,
            "environment": camera.environment or "normal",
            "ground_truth_count": 0, "detected_event_count": len(events),
            "tp": 0, "tn": 0, "fp": 0, "fn": 0,
            "accuracy": None, "detection_rate": None,
            "average_response_time_ms": round(sum(response_values) / len(response_values), 2) if response_values else None,
            "matches": [],
        }
    positives = [item for item in truths if item.event_type != "normal"]
    negatives = [item for item in truths if item.event_type == "normal"]
    unmatched_events = set(range(len(events)))
    matches = []
    for truth in positives:
        candidates = [
            (index, abs((event.video_seconds or 0) - truth.video_seconds))
            for index, event in enumerate(events)
            if index in unmatched_events and event.event_type == truth.event_type
            and abs((event.video_seconds or 0) - truth.video_seconds) <= truth.tolerance_seconds
        ]
        if candidates:
            index, delta = min(candidates, key=lambda item: item[1])
            unmatched_events.remove(index)
            matches.append({"ground_truth_id": truth.id, "event_id": events[index].id, "delta_seconds": round(delta, 3)})
    tp = len(matches)
    fn = len(positives) - tp
    fp = len(unmatched_events)
    tn = sum(
        1 for truth in negatives
        if not any(abs((event.video_seconds or 0) - truth.video_seconds) <= truth.tolerance_seconds for event in events)
    )
    total = tp + tn + fp + fn
    response_values = [event.response_time_ms for event in events if event.response_time_ms is not None]
    return {
        "camera_id": camera_id,
        "video_name": camera.name,
        "environment": camera.environment or "normal",
        "ground_truth_count": len(truths),
        "detected_event_count": len(events),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": round((tp + tn) / total * 100, 2) if total else None,
        "detection_rate": round(tp / len(positives) * 100, 2) if positives else None,
        "average_response_time_ms": round(sum(response_values) / len(response_values), 2) if response_values else None,
        "matches": matches,
    }


@router.get("/summary/all")
def environment_summary(db: Session = Depends(get_db)):
    grouped: dict[str, dict] = {}
    for camera in db.query(models.Camera).all():
        result = calculate(camera.id, db)
        if result["ground_truth_count"] == 0:
            continue
        environment = result["environment"]
        row = grouped.setdefault(environment, {"environment": environment, "videos": 0, "tp": 0, "tn": 0, "fp": 0, "fn": 0, "response_values": []})
        row["videos"] += 1
        for key in ("tp", "tn", "fp", "fn"):
            row[key] += result[key]
        if result["average_response_time_ms"] is not None:
            row["response_values"].append(result["average_response_time_ms"])
    output = []
    for row in grouped.values():
        total = row["tp"] + row["tn"] + row["fp"] + row["fn"]
        values = row.pop("response_values")
        output.append({
            **row,
            "accuracy": round((row["tp"] + row["tn"]) / total * 100, 2) if total else None,
            "average_response_time_ms": round(sum(values) / len(values), 2) if values else None,
        })
    return output


@router.get("/{camera_id}")
def evaluate(camera_id: int, db: Session = Depends(get_db)):
    return calculate(camera_id, db)


@router.get("/{camera_id}/csv")
def export_csv(camera_id: int, db: Session = Depends(get_db)):
    result = calculate(camera_id, db)
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["video", "environment", "ground_truth", "detected_events", "TP", "TN", "FP", "FN", "accuracy_percent", "detection_rate_percent", "average_response_time_ms"])
    writer.writerow([result["video_name"], result["environment"], result["ground_truth_count"], result["detected_event_count"], result["tp"], result["tn"], result["fp"], result["fn"], result["accuracy"], result["detection_rate"], result["average_response_time_ms"]])
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=evaluation_video_{camera_id}.csv"})
