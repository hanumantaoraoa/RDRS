import csv
import io
import json
import os
import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import AlertRecord, FileEventRecord, ProcessRecord
from app.core.config import load_config

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
    return db.query(FileEventRecord).order_by(FileEventRecord.timestamp.desc()).limit(100).all()@api_router.post("/export/gh-pages")
def export_gh_pages():
    """Generates the static JSON state for the GitHub Pages host monitoring webpage."""
    session = SessionLocal()
    alerts = session.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).all()
    events_count = session.query(FileEventRecord).count()

    payload = {
        "last_updated": str(datetime.datetime.utcnow()),
        "total_events": events_count,
        "alerts": [{"timestamp": str(a.timestamp), "id": a.pid, "process": a.process_name, "score": a.threat_score,
                    "desc": a.description} for a in alerts]
    }
    session.close()

    out_dir = config.system.gh_pages_dir
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "dashboard_data.json"), "w") as f:
        json.dump(payload, f, indent=2)

    return JSONResponse({"status": "exported", "target_dir": out_dir})


