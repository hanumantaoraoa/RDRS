import os
import shutil
from datetime import datetime, timedelta
from collections import deque
from loguru import logger
from rdrs.app.core.config import AppConfig
from rdrs.app.core.models import FileEventModel
from rdrs.app.database.connection import DBFileEvent, DBAlert, DBIncident

class DetectionEngine:
    def __init__(self, config: AppConfig, session_factory):
        self.config = config
        self.Session = session_factory
        self.event_history = deque() # Memory tracking sliding time-window (FR-6)

    def process_new_event(self, event: FileEventModel):
        session = self.Session()
        try:
            # Persistent event entry mapping (FR-5)
            db_event = DBFileEvent(
                event_type=event.event_type,
                src_path=event.src_path,
                dest_path=event.dest_path,
                timestamp=event.timestamp,
                entropy=event.entropy,
                pid=event.pid,
                process_name=event.process_name
            )
            session.add(db_event)
            session.commit()
            
            self.event_history.append(event)
            self._evaluate_sliding_window(event, session)
        except Exception as e:
            logger.error(f"Error handling engine event pipeline execution: {e}")
            session.rollback()
        finally:
            session.close()

    def _evaluate_sliding_window(self, current_event: FileEventModel, session):
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.config.analysis.window_seconds)
        
        # Prune dead old history metrics
        while self.event_history and self.event_history[0].timestamp < cutoff:
            self.event_history.popleft()

        # Compute dynamic scores (FR-7)
        score = 0
        high_entropy_count = 0
        type_counts = {"create": 0, "modify": 0, "delete": 0, "rename": 0}

        for ev in self.event_history:
            t = ev.event_type.lower()
            if t in type_counts:
                type_counts[t] += 1
            if ev.entropy >= self.config.analysis.high_entropy_threshold:
                high_entropy_count += 1

        score += type_counts["create"] * self.config.weights.file_create
        score += type_counts["modify"] * self.config.weights.file_modify
        score += type_counts["delete"] * self.config.weights.file_delete
        score += type_counts["rename"] * self.config.weights.file_rename
        
        if high_entropy_count > 0:
            score += self.config.weights.high_entropy
        if len(self.event_history) >= self.config.analysis.max_events_per_window:
            score += self.config.weights.rapid_activity

        final_score = min(score, 100)

        # Trigger responses if threats cross the 50 score line (FR-8)
        if final_score >= 50:
            msg = f"Ransomware behavioral threshold crossed. Activity footprint: {type_counts}, High Entropy items: {high_entropy_count}"
            logger.warning(f"[ALERT] Score: {final_score} | {msg} | Target PID: {current_event.pid}")
            
            alert = DBAlert(threat_score=final_score, description=msg, trigger_pid=current_event.pid)
            session.add(alert)
            session.commit()

            # Trigger isolation protection backup simulations (FR-9)
            quarantine_dst = None
            if current_event.src_path and os.path.exists(current_event.src_path):
                try:
                    fname = f"{int(datetime.utcnow().timestamp())}_{os.path.basename(current_event.src_path)}"
                    quarantine_dst = os.path.join(self.config.system.quarantine_directory, fname)
                    shutil.copy2(current_event.src_path, quarantine_dst)
                    logger.info(f"[QUARANTINE-SIM] Target evidence saved securely to: {quarantine_dst}")
                except Exception as ex:
                    logger.error(f"Failed to execute evidence quarantine sequence copy: {ex}")

            incident = DBIncident(assigned_score=final_score, quarantine_path=quarantine_dst)
            session.add(incident)
            session.commit()
