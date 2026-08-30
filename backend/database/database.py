"""
SQLite for the prototype. Swap DATABASE_URL for a postgres:// URL later —
everything else (models, sessions, queries) stays the same.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./school_guardian.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models so they're registered on Base before create_all
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    # Minimal SQLite migrations for existing prototype databases.
    migrations = {
        "cameras": {
            "environment": "ALTER TABLE cameras ADD COLUMN environment VARCHAR DEFAULT 'normal'",
        },
        "events": {
            "video_seconds": "ALTER TABLE events ADD COLUMN video_seconds FLOAT",
            "response_time_ms": "ALTER TABLE events ADD COLUMN response_time_ms FLOAT",
            "review_status": "ALTER TABLE events ADD COLUMN review_status VARCHAR DEFAULT 'pending'",
            "reviewed_by": "ALTER TABLE events ADD COLUMN reviewed_by VARCHAR",
            "reviewed_at": "ALTER TABLE events ADD COLUMN reviewed_at DATETIME",
        },
    }
    with engine.begin() as connection:
        for table, columns in migrations.items():
            existing = {row[1] for row in connection.execute(text(f"PRAGMA table_info({table})"))}
            for column, statement in columns.items():
                if column not in existing:
                    connection.execute(text(statement))
    db = SessionLocal()
    try:
        demo = db.query(models.Camera).filter(models.Camera.name == "CAM DEMO").first()
        if demo is None:
            demo = models.Camera(
                name="CAM DEMO",
                location="School Road / Entrance",
                source="mp4",
                source_uri="storage/videos/demo_school_guardian.mp4",
                status="online",
            )
            db.add(demo)
            db.flush()
            db.add(models.Zone(
                camera_id=demo.id,
                name="Restricted pavement zone",
                polygon=[[0.02, 0.42], [0.98, 0.42], [0.98, 0.78], [0.02, 0.78]],
                zone_type="restricted",
                loitering_threshold=10,
            ))
            db.commit()
        settings = db.query(models.SystemSettings).first()
        if settings is None:
            db.add(models.SystemSettings(
                detection_threshold=0.5,
                loitering_threshold=10,
                alert_settings={"human_verification_required": True},
            ))
            db.commit()
    finally:
        db.close()
