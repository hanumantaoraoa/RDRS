from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.routes import router as core_router
from app.database.connection import SessionLocal
from app.database.models import AlertRecord, FileEventRecord

app = FastAPI(title="RDRS Operations Hub Dashboard")
app.include_router(core_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
def render_gui_dashboard():
    db = SessionLocal()
    try:
        alerts = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).limit(10).all()
        events = db.query(FileEventRecord).order_by(FileEventRecord.timestamp.desc()).limit(15).all()

        last_alert = alerts[0] if alerts else None
        risk = last_alert.threat_score if last_alert else 0.0
        level = last_alert.threat_level if last_alert else "Normal"

        level_color = "#10b981" if level == "Normal" else "#f59e0b" if level == "Warning" else "#ef4444"

        alert_rows = "".join([
                                 f"<tr style='border-bottom: 1px solid #475569;'><td>{a.timestamp.strftime('%H:%M:%S')}</td><td><span style='color:{'#ef4444' if a.threat_level == 'Critical' else '#f59e0b'}'>{a.threat_level}</span></td><td>{a.threat_score}</td><td>{a.reason}</td><td>{a.suspect_process}</td></tr>"
                                 for a in alerts])

        event_rows = "".join([
                                 f"<tr style='border-bottom: 1px solid #334155;'><td>{e.timestamp.strftime('%H:%M:%S')}</td><td>{e.event_type.upper()}</td><td>{e.file_path}</td><td>{e.entropy:.4f}</td></tr>"
                                 for e in events])
    finally:
        db.close()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RDRS Console</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1e293b; padding-bottom: 16px; margin-bottom: 24px; }}
            .status-card {{ background-color: #1e293b; border-radius: 8px; padding: 20px; display: flex; gap: 40px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }}
            .stat {{ display: flex; flex-direction: column; }}
            .stat-lbl {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }}
            .stat-val {{ font-size: 28px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 12px; text-align: left; background-color: #1e293b; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 12px 16px; font-size: 14px; }}
            th {{ background-color: #334155; color: #f8fafc; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; }}
            h2 {{ font-size: 18px; color: #f1f5f9; margin-top: 32px; margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0; font-size: 24px; color: #f8fafc;">🛡️ RDRS Security Operations Console</h1>
                <span style="background-color: #1e293b; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #a855f7; font-weight: bold; border: 1px solid #4c1d95;">SIMULATION MATRIX MODE</span>
            </div>

            <div class="status-card">
                <div class="stat">
                    <span class="stat-lbl">System State</span>
                    <span class="stat-val" style="color: #3b82f6;">ACTIVE MONITORING</span>
                </div>
                <div class="stat">
                    <span class="stat-lbl">Calculated Metric Risk</span>
                    <span class="stat-val" style="color: {level_color};">{risk:.1f} / 100</span>
                </div>
                <div class="stat">
                    <span class="stat-lbl">Evaluated Threat Level</span>
                    <span class="stat-val" style="color: {level_color};">{level}</span>
                </div>
            </div>

            <h2>⚠️ Recent Flagged Security Anomalies ({len(alerts)})</h2>
            <table>
                <tr><th>Timestamp</th><th>Threat Level</th><th>Score</th><th>Reason Evaluation Context</th><th>Suspect Runtime Executable</th></tr>
                {alert_rows if alert_rows else "<tr><td colspan='5' style='color:#64748b; text-align:center;'>No structural anomalies logged across active monitoring operations windows.</td></tr>"}
            </table>

            <h2>📊 Real-Time File Telemetry Streams System Logs</h2>
            <table>
                <tr><th>Timestamp</th><th>Operation Type</th><th>Target Absolute System File Path Location Address</th><th>Calculated Entropy</th></tr>
                {event_rows if event_rows else "<tr><td colspan='4' style='color:#64748b; text-align:center;'>Awaiting filesystem hook event registration signals...</td></tr>"}
            </table>
        </div>
    </body>
    </html>
    """
