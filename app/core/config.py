import os
import yaml
from pydantic import BaseModel
from typing import List

class SystemConfig(BaseModel):
    environment: str
    quarantine_dir: str
    watch_paths: List[str]
    gh_pages_dir: str

class ThresholdConfig(BaseModel):
    entropy_critical: float
    entropy_warning: float
    time_window_secs: int
    max_files_per_window: int
    critical_threat_score: float

class WeightConfig(BaseModel):
    frequency_weight: float
    rename_weight: float
    entropy_weight: float
    cpu_weight: float
    unknown_program_weight: float

class DatabaseConfig(BaseModel):
    url: str = "sqlite:///data/rdrs.db"

class ServerConfig(BaseModel):
    host: str
    port: int

class AppConfig(BaseModel):
    system: SystemConfig
    thresholds: ThresholdConfig
    weights: WeightConfig
    database: DatabaseConfig
    server: ServerConfig

def load_config(path: str = "config.yaml") -> AppConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration profile not resolved at: {path}")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)
