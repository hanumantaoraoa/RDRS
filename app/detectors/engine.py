import os
import shutil
import psutil
from datetime import datetime, timedelta
from loguru import logger
from app.core.config import load_config
from app.database.connection import SessionLocal
from app.database.models import FileEventRecord, AlertRecord, ProcessRecord


class DetectionEngine:
    def __init__(self):
        self.config = load_config()

    def process_telemetry(self, current_event: FileEventRecord):
        db = SessionLocal()
        try:
            window_start = datetime.utcnow() - timedelta(seconds=self.config.thresholds.time_window_secs)
            recent_events = db.query(FileEventRecord).filter(
                FileEventRecord.timestamp >= window_start
            ).all()

            if not recent_events:
                return

            total_events = len(recent_events)
            high_entropy_events = sum(
                1 for e in recent_events if e.entropy and e.entropy >= self.config.thresholds.entropy_warning)
            rename_events = sum(1 for e in recent_events if e.event_type == "renamed")

            # Rule Evaluation Flag Identifiers
            burst_detected = total_events >= self.config.thresholds.max_files_per_window
            mass_rename_detected = rename_events >= (self.config.thresholds.max_files_per_window / 2)
            encryption_signature = high_entropy_events >= (self.config.thresholds.max_files_per_window / 2)

            # Metric evaluations via psutil
            cpu_spike = False
            suspect_proc_name = "Unknown Activity Engine"

            active_procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 40.0:
                        cpu_spike = True
                        suspect_proc_name = pinfo['name']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Threat Scoring Rules Engine Model Equation
            raw_score = 0.0
            reasons = []

            if burst_detected:
                raw_score += self.config.weights.frequency_weight
                reasons.append("High frequency modification event burst pattern detected.")
            if mass_rename_detected:
                raw_score += self.config.weights.rename_weight
                reasons.append("Mass manipulation/extension rename transformations observed.")
            if encryption_signature:
                raw_score += self.config.weights.entropy_weight
                reasons.append("High entropy payload footprint identified across targets.")
            if cpu_spike:
                raw_score += self.config.weights.cpu_weight
                reasons.append("Correlated resource computational execution utilization spike observed.")

            threat_score = min(raw_score, 100.0)

            # Severity Band Classifications
            if threat_score >= self.config.thresholds.critical_threat_score:
                threat_level = "Critical"
            elif threat_score >= 40.0:
                threat_level = "Warning"
            else:
                threat_level = "Normal"

            if threat_level in ["Warning", "Critical"]:
                reason_summary = " | ".join(reasons)
                logger.warning(
                    f"[ALERT MATCHED] Risk Calculated: {threat_score} [{threat_level}] - Reason: {reason_summary}")

                alert = AlertRecord(
                    threat_score=threat_score,
                    threat_level=threat_level,
                    reason=reason_summary,
                    suspect_process=suspect_proc_name,
                    status="Simulated Interdiction" if self.config.system.environment == "simulation" else "Active Isolation"
                )
                db.add(alert)
                db.commit()

                # Context Snapshots Logging
                self.log_offending_processes(db)

                # Active Simulation Quarantine Strategy Isolation
                if threat_level == "Critical" and self.config.system.environment == "simulation":
                    self.quarantine_target(current_event.file_path)

        except Exception as e:
            logger.error(f"Error executing threat processing calculations: {e}")
        finally:
            db.close()

    def log_offending_processes(self, db_session):
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'exe']):
            try:
                info = proc.info
                if info['cpu_percent'] and info['cpu_percent'] > 5.0:
                    prec = ProcessRecord(
                        pid=info['pid'],
                        name=info['name'] or "Unknown Resource Driver",
                        cpu_percent=info['cpu_percent'],
                        memory_percent=info['memory_percent'],
                        exe_path=info['exe']
                    )
                    db_session.add(prec)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        db_session.commit()

    def quarantine_target(self, file_path: str):
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return
        os.makedirs(self.config.system.quarantine_dir, exist_ok=True)
        try:
            destination = os.path.join(self.config.system.quarantine_dir, os.path.basename(file_path))
            shutil.copy2(file_path, destination)
            logger.info(
                f"[AUDIT LOG ENTRY] Simulation Mode Action: Safely isolated artifact to repository vault: {destination}")
        except Exception as e:
            logger.error(f"Failed to cleanly clone target file structure details to sandbox: {e}")