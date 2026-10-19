import os
import sys
from loguru import logger


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger.remove()

    # Standard STDOUT Console Sync Terminal Output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )

    # Specific Rotated Event Log Configurations
    logger.add("logs/system.log", rotation="10 MB", level="INFO")
    logger.add("logs/events.log", rotation="10 MB", level="DEBUG")
    logger.add("logs/alerts.log", rotation="5 MB", level="WARNING")
    logger.add("logs/audit.log", rotation="5 MB", level="INFO")
