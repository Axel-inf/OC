from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from config.settings import DATABASE_URL
from database.models import Base

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialise la base de données"""
    Base.metadata.create_all(bind=engine)
    _ensure_calendar_event_columns()


def _ensure_calendar_event_columns() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if 'calendar_events' not in table_names:
        return

    columns = {column['name'] for column in inspector.get_columns('calendar_events')}
    
    with engine.begin() as connection:
        if 'is_hidden' not in columns:
            connection.execute(text('ALTER TABLE calendar_events ADD COLUMN is_hidden BOOLEAN NOT NULL DEFAULT 0'))
        if 'source_event_id' not in columns:
            connection.execute(text('ALTER TABLE calendar_events ADD COLUMN source_event_id INTEGER'))

def get_db() -> Session:
    """Retourne une session de base de données"""
    return SessionLocal()