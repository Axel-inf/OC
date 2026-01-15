from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import DATABASE_URL
from database.models import Base

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialise la base de données"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Retourne une session de base de données"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()