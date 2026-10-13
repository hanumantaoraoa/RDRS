import os
import sys
from loguru import logger

def setup_logger(log_dir: str):
    """ Setup rotating log files (system, events, alerts, errors, audit)."""
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)
    logger.remove()

    # Shared common formatting template
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level:7} | {message}"

    # Standard console logging format
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:7}</level> | <cyan>{message}</cyan>", level="INFO")

    # 1. System Log: Core application lifecycles
    logger.add(os.path.join(log_dir, "system.log"), rotation="5 MB", retention="5 days", level="DEBUG",
               filter=lambda record: "system" in record["extra"])

    # 2. Events Log: Raw telemetry and filesystem streams
    logger.add(os.path.join(log_dir, "events.log"), rotation="10 MB", retention="5 days", level="DEBUG",
               filter=lambda record: "event" in record["extra"])

    # 3. Alerts Log: Generated threat intelligence detections
    logger.add(os.path.join(log_dir, "alerts.log"), rotation="5 MB", retention="7 days", level="WARNING",
               filter=lambda record: "alert" in record["extra"])

    # 4. Errors Log: Catastrophic errors and exceptions captured
    logger.add(os.path.join(log_dir, "errors.log"), rotation="5 MB", retention="10 days", level="ERROR",
               filter=lambda record: record["level"].name in ["ERROR", "CRITICAL"])

    # 5. Audit Log: Administrative controls and compliance steps
    logger.add(os.path.join(log_dir, "audit.log"), rotation="5 MB", retention="30 days", level="INFO",
               filter=lambda record: "audit" in record["extra"])

    return logger