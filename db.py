from sqlmodel import SQLModel, create_engine, Session
import os

DB_URL = os.getenv("DB_URL", "sqlite:///timetable.db")
engine = create_engine(DB_URL, echo=False)

def init_db():
    import models  # ✅ works as top-level
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
