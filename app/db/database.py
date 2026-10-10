import os
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


def init_engine() -> Engine:
    db_url = settings.DATABASE_URL
    if db_url and db_url.startswith("postgresql"):
        try:
            eng = create_engine(
                db_url,
                echo=settings.DEBUG,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 2}
            )
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            return eng
        except Exception:
            # Fallback to sqlite if postgres is not active
            pass

    # Fallback / standalone SQLite database
    sqlite_url = "sqlite:///./trustroute.db"
    return create_engine(sqlite_url, echo=settings.DEBUG, connect_args={"check_same_thread": False})


engine = init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection(target_engine: Optional[Engine] = None) -> bool:
    """Helper to verify database connection status."""
    eng = target_engine or engine
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
