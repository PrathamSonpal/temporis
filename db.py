# works both locally and on Railway
try:
    import models
except ImportError:
    from . import models

DB_URL = os.getenv("DB_URL", "sqlite:///timetable.db")
engine = create_engine(DB_URL, echo=False)

def init_db():
    from . import models  # noqa: F401
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
