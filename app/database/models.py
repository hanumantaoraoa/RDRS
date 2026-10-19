from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FileEventRecord(Base):
    __tablename__ = 'file_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)  # created, modified, deleted, renamed
    file_path = Column(String, nullable=False)
    extension = Column(String, nullable=True)
    entropy = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ProcessRecord(Base):
    __tablename__ = 'processes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    cpu_percent = Column(Float, nullable=True)
    memory_percent = Column(Float, nullable=True)
    exe_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AlertRecord(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    threat_score = Column(Float, nullable=False)
    threat_level = Column(String, nullable=False) # Normal, Warning, Critical
    reason = Column(String, nullable=False)
    suspect_process = Column(String, nullable=True)
    status = Column(String, default="Simulated Action")
    timestamp = Column(DateTime, default=datetime.utcnow)
