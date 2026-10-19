import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger
from app.core.entropy import calculate_file_entropy
from app.database.connection import SessionLocal
from app.database.models import FileEventRecord


class SystemActivityHandler(FileSystemEventHandler):
    def __init__(self, engine_callback):
        self.engine_callback = engine_callback

    def record_and_dispatch(self, event_type: str, src_path: str):
        if os.path.isdir(src_path) or "rdrs.db" in src_path or "quarantine" in src_path:
            return

        db = SessionLocal()
        try:
            _, ext = os.path.splitext(src_path)
            entropy = calculate_file_entropy(src_path) if event_type in ["created", "modified"] else 0.0

            record = FileEventRecord(
                event_type=event_type,
                file_path=os.path.abspath(src_path),
                extension=ext,
                entropy=entropy,
                timestamp=datetime.utcnow()
            )
            db.add(record)
            db.commit()

            logger.debug(f"[TELEMETRY] {event_type.upper()} captured for target: {src_path}")
            self.engine_callback(record)
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}")
        finally:
            db.close()

    def on_created(self, event):
        self.record_and_dispatch("created", event.src_path)

    def on_modified(self, event):
        self.record_and_dispatch("modified", event.src_path)

    def on_deleted(self, event):
        self.record_and_dispatch("deleted", event.src_path)

    def on_moved(self, event):
        self.record_and_dispatch("renamed", event.dest_path)


def start_monitor(paths: list, engine_callback) -> Observer:
    observer = Observer()
    handler = SystemActivityHandler(engine_callback)
    for path in paths:
        os.makedirs(path, exist_ok=True)
        observer.schedule(handler, path, recursive=True)
    observer.start()
    return observer
