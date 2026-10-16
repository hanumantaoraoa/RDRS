from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import AlertRecord, FileEventRecord, ProcessRecord

router = APIRouter()


def get_db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health_endpoint():
    return {"status": "operational", "engine": "RDRS Rule Platform Core V1.0"}


@router.get("/status")
def status_endpoint(db: Session = Depends(get_db_context)):
    total_events = db.query(FileEventRecord).count()
    total_alerts = db.query(AlertRecord).count()
    last_alert = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).first()

    return {
        "active_status": "MONITORING",
        "total_analyzed_events": total_events,
        "incidents_logged": total_alerts,
        "current_system_risk": last_alert.threat_score if last_alert else 0.0,
        "current_threat_level": last_alert.threat_level if last_alert else "Normal"
    }


@router.get("/alerts")
def alerts_endpoint(db: Session = Depends(get_db_context)):
    return db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).limit(50).all()


@router.get("/events")
def events_endpoint(db: Session = Depends(get_db_context)):
    return db.query(FileEventRecord).order_by(FileEventRecord.timestamp.desc()).limit(100).all()
