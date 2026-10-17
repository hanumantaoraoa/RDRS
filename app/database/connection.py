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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_SessionMaker = None

def init_db(db_url: str):
    # FR-5: Initialize SQLite Database
    global _SessionMaker
    engine = create_engine(db_url, connect_args={"check_same_thread": False} if "sqlite" in db_url else {})
    Base.metadata.create_all(engine)
    _SessionMaker = sessionmaker(bind=engine)

def get_session():
    if _SessionMaker is None:
        raise RuntimeError("Database engine has not been initialized.")
    return _SessionMaker()
