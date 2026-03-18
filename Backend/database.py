"""
database.py
-----------
Database connection and session management using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # Set to True to log all SQL queries (useful for debugging)
)

# Session factory — use this to get a DB session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def get_db():
    """
    Dependency that provides a database session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
