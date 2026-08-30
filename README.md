# AI School Guardian

AI-assisted recorded-video monitoring for school safety. The system detects
predefined events only (restricted-zone entry, loitering, potential risk
objects) and forwards them for **human verification** — it never decides
on its own whether someone is dangerous.

This edition intentionally uses uploaded **MP4 recordings instead of live,
webcam, or RTSP footage**. The included demo video is wired into the dashboard and the backend runs
YOLO person detection, ByteTrack tracking, restricted-zone checks, and exports
an annotated browser-ready MP4 with an analysis summary.

## What's here right now

- **frontend/** — Next.js 14 + Tailwind. Includes Overview, MP4 Library,
  per-video analysis, still-image upload and GPU analysis, polygon Zone Editor, Event Log filters and human review,
  Analytics, Ground Truth/Evaluation, CSV export, and Settings.
- **backend/** — FastAPI + SQLite (SQLAlchemy). Uploaded MP4 files are registered
  as video sources. Analysis creates database events, browser-ready H.264 output,
  snapshots, restricted-zone entries, video-clock-based loitering events,
  Potential Risk Object candidates, response-time metrics, and review state.
- **backend/ai/** — YOLO person detection and persistent ByteTrack IDs are wired
  through `PersonDetector.track`; restricted-zone and loitering helpers remain reusable.
- **backend/ai/risk_object.py** — dedicated firearm detection plus COCO risk-object
  screening, deliberately isolated from the core pipeline and always requiring
  human verification (never asserts a confirmed weapon classification).

## Run it

**Backend**
```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
The base install includes YOLOv8 + ByteTrack. If the model cannot load, the
person pipeline falls back to OpenCV; Potential Risk Object screening remains
disabled rather than fabricating a result. COCO screens knife, scissors, and
baseball bat candidates. `backend/models/firearm-yolov8n.pt` is a dedicated
single-class firearm model used for gun candidates. Large-box and person-
association filters reduce false alarms from stair rails and background objects.
Every candidate always requires human verification.

Recorded-video firearm screening also uses an overlapping-tile deep scan for
small/distant objects and temporal confirmation across frames. A normal
candidate must recur before an Event is created; only an exceptionally strong
candidate can alert immediately. This reduces one-frame false alarms while
still allowing unattended risk objects to be surfaced for review.

Firearm weights: [Subh775/Firearm_Detection_Yolov8n](https://huggingface.co/Subh775/Firearm_Detection_Yolov8n)
(repository metadata currently lists AGPL-3.0). Review the model license before redistribution or
commercial deployment.

For the GTX 1050 / Pascal Windows setup, install `requirements-gpu.txt`.
It uses the CUDA 11.8 PyTorch wheels, which run on newer NVIDIA drivers while
retaining support for the GPU's compute capability. The detectors select GPU 0
automatically and fall back to CPU when CUDA is unavailable.

API docs at http://localhost:8000/docs — the interactive Swagger UI is the
fastest way to poke at `/api/cameras`, `/api/events`, `/api/zones`.

**Frontend**
```
cd frontend
npm install
npm run dev
```
Dashboard at http://localhost:3000.

## Build order (from the project plan)

1. ✅ Frontend Dashboard shell
2. ✅ Backend FastAPI structure
3. ✅ Connect demo analysis frontend → backend
4. ✅ Upload/serve Video (MP4)
5. ✅ YOLOv8 person detection (`backend/ai/detector.py`)
6. ✅ ByteTrack tracking (via Ultralytics persistent tracker)
7. ✅ Restricted Zone (`backend/ai/restricted_zone.py` — ready to use)
8. ✅ Loitering (`backend/ai/loitering.py` — ready to use)
9. ✅ Restricted-zone entry summary in the analysis pipeline
10. ✅ WebSocket real-time alerts (`backend/api/ws.py`)
11. ✅ Statistics endpoint
12. ✅ MP4 Library and upload workflow
13. ✅ Polygon Zone Editor, Event Log, Analytics, and Settings
14. ✅ Potential Risk Object candidate detection + mandatory human review
15. ⬜ Person Re-ID (out of scope for the recorded-video MVP)

Live Camera, webcam, and RTSP pages are deliberately excluded from this MP4-only edition.
The Dashboard loops the latest annotated H.264 result for each video source;
before a source has been analyzed it loops the original MP4 and labels it accordingly.

## Evaluation workflow

Tag each uploaded MP4 as Normal Lighting, Low Light, or Partial Occlusion.
After analysis, add Ground Truth checkpoints in the Evaluation page. A positive
checkpoint is matched by event type and video timestamp tolerance; a Normal
checkpoint counts as TN when no event appears in its window. The page calculates
TP/TN/FP/FN, Accuracy, Detection Rate, and average Response Time and exports CSV.

## Database

SQLite file (`backend/school_guardian.db`) is created automatically on
first run. Tables: `cameras`, `zones`, `events`, `system_settings` — see
`backend/database/models.py`. Switch to Postgres later by changing
`DATABASE_URL` in `backend/database/database.py`; nothing else changes.
