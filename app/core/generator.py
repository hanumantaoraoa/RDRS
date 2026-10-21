import json
import csv
import os
from app.database.connection import SessionLocal
from app.database.models import AlertRecord


def generate_reports(base_dir: str = "reports"):
    os.makedirs(base_dir, exist_ok=True)
    db = SessionLocal()
    try:
        alerts = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).all()

        # 1. Output Clean Structured JSON Format
        json_data = [
            {
                "incident_id": a.id,
                "threat_score": a.threat_score,
                "threat_level": a.threat_level,
                "reason_matrix": a.reason,
                "suspect_binary": a.suspect_process,
                "status_action": a.status,
                "timestamp": str(a.timestamp)
            } for a in alerts
        ]
        with open(os.path.join(base_dir, "incident_report.json"), "w") as jf:
            json.dump(json_data, jf, indent=4)

        # 2. Output Consolidated Flat CSV Schema Data Log Sheets
        with open(os.path.join(base_dir, "incident_report.csv"), "w", newline="") as cf:
            writer = csv.writer(cf)
            writer.writerow(
                ["INCIDENT_ID", "THREAT_SCORE", "THREAT_LEVEL", "DETERMINATION_REASON", "SUSPECT_PROCESS", "STATUS",
                 "TIMESTAMP"])
            for a in alerts:
                writer.writerow(
                    [a.id, a.threat_score, a.threat_level, a.reason, a.suspect_process, a.status, a.timestamp])
    finally:
        db.close()
