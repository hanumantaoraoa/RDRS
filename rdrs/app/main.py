import sys
import os
import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Correct application routing resolution paths lookup hooks
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app.core.config import load_config
from app.core.logger import setup_logger
from app.database.connection import init_db, DBFileEvent, DBAlert
from app.detectors.engine import DetectionEngine
from app.detectors.monitor import start_file_monitor
from app.api.routes import router as api_router, init_api_session, get_db
from app.dashboard.dashboard import get_dashboard_html

# 1. Load Configurations (FR-1)
config = load_config("rdrs/config.yaml")
logger = setup_logger(config.system.log_dir)

# 2. Database Connection Initialization (FR-5)
SessionMaker = init_db(config.system.database_url)
init_api_session(SessionMaker)

# 3. Detection Engine Strategy Instantiation (FR-6, FR-7, FR-8)
engine = DetectionEngine(config, SessionMaker)

# 4. File-System Event Watcher Core Bootstrapping (FR-2, FR-4)
observer_worker = start_file_monitor(config, engine, SessionMaker)

# 5. REST API Layer Assembly Construction (FR-10)
app = FastAPI(title="Ransomware Detection and Response System Endpoint Core")
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=get_dashboard_html)
def render_live_web_dashboard(db: Session = Depends(get_db)):
    """Serves the dynamic management control frontend interface view dashboard."""
    events = db.query(DBFileEvent).order_by(DBFileEvent.id.desc()).limit(15).all()
    alerts = db.query(DBAlert).order_by(DBAlert.id.desc()).limit(15).all()
    return get_dashboard_html(events, alerts)

if __name__ == "__main__":
    logger.info("Initializing active protection layers over operational API engine frames...")
    try:
        uvicorn.run(app, host=config.api.host, port=config.api.port, log_level="warning")
    finally:
        logger.info("Stopping real-time context collection daemon background workers...")
        observer_worker.stop()
        observer_worker.join()

