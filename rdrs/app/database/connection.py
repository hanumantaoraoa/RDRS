import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.core.config import load_config

config = load_config()
db_path_raw = config.database.url.replace("sqlite:///", "")
db_dir = os.path.dirname(db_path_raw)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

engine = create_engine(config.database.url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
