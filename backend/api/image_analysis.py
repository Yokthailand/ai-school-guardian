"""GPU-assisted analysis for uploaded still images."""
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from ai.detector import PersonDetector
from ai.risk_object import RiskObjectDetector

router = APIRouter(prefix="/api", tags=["image analysis"])
BACKEND_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BACKEND_DIR / "storage" / "processed" / "images"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_BYTES = 15 * 1024 * 1024
PERSON_DETECTOR = PersonDetector(conf_threshold=0.35)
RISK_DETECTOR = RiskObjectDetector(conf_threshold=0.35)


@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if file.content_type not in ALLOWED_TYPES and suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only JPG, PNG, and WebP images are supported")
    content = await file.read()
    if not content or len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(400, "Image must be between 1 byte and 15 MB")

    import cv2
    import numpy as np

    frame = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(400, "The uploaded file is not a readable image")

    started = perf_counter()
    people = PERSON_DETECTOR.detect(frame)
    risks = RISK_DETECTOR.detect(frame, person_boxes=[person["bbox"] for person in people])

    detections = []
    for index, person in enumerate(people, start=1):
        x1, y1, x2, y2 = map(int, person["bbox"])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (61, 255, 154), 2)
        cv2.putText(frame, f"PERSON #{index} {person['confidence']:.0%}", (x1, max(20, y1 - 7)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (61, 255, 154), 2)
        detections.append({
            "type": "person", "label": "person", "person_id": index,
            "confidence": round(person["confidence"], 4),
            "bbox": [round(value, 1) for value in person["bbox"]],
            "alert_level": "NORMAL",
        })

    for risk in risks:
        x1, y1, x2, y2 = map(int, risk["bbox"])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 239), 3)
        cv2.putText(frame, f"POTENTIAL RISK: {risk['label'].upper()} - REVIEW", (x1, max(24, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 239), 2)
        detections.append({
            "type": "risk_object", "label": risk["label"],
            "confidence": round(risk["confidence"], 4),
            "bbox": [round(value, 1) for value in risk["bbox"]],
            "alert_level": "ALERT", "requires_human_verification": True,
        })

    elapsed_ms = round((perf_counter() - started) * 1000, 2)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"analyzed_{uuid4().hex}.jpg"
    cv2.imwrite(str(OUTPUT_DIR / filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return {
        "status": "completed",
        "processed_image_url": f"/media/processed/images/{filename}",
        "width": int(frame.shape[1]), "height": int(frame.shape[0]),
        "people_count": len(people), "risk_object_count": len(risks),
        "alert_level": "ALERT" if risks else "NORMAL",
        "response_time_ms": elapsed_ms,
        "person_detector_engine": PERSON_DETECTOR.engine,
        "risk_detector_engine": RISK_DETECTOR.engine,
        "human_verification_required": bool(risks),
        "detections": detections,
    }
