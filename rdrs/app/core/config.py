import os
import yaml
from pydantic import BaseModel, Field

class SystemConfig(BaseModel):
    monitored_directory: str
    quarantine_directory: str
    database_url: str
    log_dir: str

class AnalysisConfig(BaseModel):
    window_seconds: int
    high_entropy_threshold: float
    max_events_per_window: int

class WeightsConfig(BaseModel):
    file_create: int
    file_modify: int
    file_delete: int
    file_rename: int
    high_entropy: int
    rapid_activity: int

class ApiConfig(BaseModel):
    host: str
    port: int

class AppConfig(BaseModel):
    system: SystemConfig
    analysis: AnalysisConfig
    weights: WeightsConfig
    api: ApiConfig

def load_config(config_path: str = "rdrs/config.yaml") -> AppConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file missing at: {config_path}")
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    config = AppConfig(**data)
    
    # Bootstrap critical working directories
    os.makedirs(config.system.monitored_directory, exist_ok=True)
    os.makedirs(config.system.quarantine_directory, exist_ok=True)
    os.makedirs(os.path.dirname(config.system.log_dir), exist_ok=True)
    
    return config
