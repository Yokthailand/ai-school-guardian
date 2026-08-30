from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database.database import init_db
from api import cameras, events, zones, statistics, ws, analyze, settings, evaluation, image_analysis

app = FastAPI(
    title="AI School Guardian API",
    description=(
        "AI-assisted CCTV monitoring for school safety. The system only "
        "detects predefined events (restricted zone entry, loitering, "
        "potential risk objects) and forwards them to authorized staff — "
        "it never autonomously judges a person as dangerous or guilty."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"^http://(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}):3000$",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cameras.router)
app.include_router(events.router)
app.include_router(zones.router)
app.include_router(statistics.router)
app.include_router(ws.router)
app.include_router(analyze.router)
app.include_router(settings.router)
app.include_router(evaluation.router)
app.include_router(image_analysis.router)

STORAGE_DIR = Path(__file__).resolve().parent / "storage"
for folder in ("videos", "processed", "snapshots", "previews"):
    (STORAGE_DIR / folder).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=STORAGE_DIR), name="media")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "service": "ai-school-guardian-api"}
