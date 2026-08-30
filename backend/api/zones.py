from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from schemas import ZoneIn, ZoneOut

router = APIRouter(prefix="/api/zones", tags=["zones"])


@router.get("", response_model=list[ZoneOut])
def list_zones(camera_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Zone)
    if camera_id is not None:
        q = q.filter(models.Zone.camera_id == camera_id)
    return q.all()


@router.post("", response_model=ZoneOut)
def create_zone(zone: ZoneIn, db: Session = Depends(get_db)):
    db_zone = models.Zone(**zone.model_dump())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.put("/{zone_id}", response_model=ZoneOut)
def update_zone(zone_id: int, zone: ZoneIn, db: Session = Depends(get_db)):
    db_zone = db.get(models.Zone, zone_id)
    if not db_zone:
        raise HTTPException(404, "Zone not found")
    for key, value in zone.model_dump().items():
        setattr(db_zone, key, value)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.delete("/{zone_id}")
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    db_zone = db.query(models.Zone).get(zone_id)
    if not db_zone:
        raise HTTPException(404, "Zone not found")
    db.delete(db_zone)
    db.commit()
    return {"deleted": zone_id}
