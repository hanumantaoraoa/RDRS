import time
import uvicorn
import threading
import sys
from app.core.config import load_config
from app.core.logger import setup_logging
from app.database.connection import init_db
from app.detectors.monitor import start_monitor
from app.detectors.engine import DetectionEngine
from app.dashboard.server import app
from app.reports.generator import generate_reports


def run_web_panel(host: str, port: int):
    uvicorn.run(app, host=host, port=port, log_level="error")


def main():
    setup_logging()
    init_db(config.database.url)
    config = load_config()

    engine = DetectionEngine()

    # Initialize Core Watchdog Telemetry Array
    monitor = start_monitor(config.system.watch_paths, engine.process_telemetry)

    # Spin up Thread Isolation for API/Dashboard Endpoint Services
    api_thread = threading.Thread(
        target=run_web_panel,
        args=(config.server.host, config.server.port),
        daemon=True
    )
    api_thread.start()

    print("\n" + "═" * 70)
    print(" 🛡️  RDRS RANSOMWARE DEFENSE PLATFORM HUB ONLINE")
    print(f" -> Local Console Dashboard Link: http://localhost:{config.server.port}")
    print(f" -> Actively Protecting Target Arrays: {config.system.watch_paths}")
    print("═" * 70 + "\n")

    try:
        while True:
            time.sleep(2)
            # Continually flush state outputs down into persistent generation file arrays
            generate_reports()
    except KeyboardInterrupt:
        print("\n[AUDIT] Security Matrix Interdiction shutdown triggered by Operator command.")
    finally:
        monitor.stop()
        monitor.join()


if __name__ == "__main__":
    main()
