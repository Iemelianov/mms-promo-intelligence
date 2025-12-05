"""
Database session utilities.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mms.db")

# Use future engine for SQLAlchemy 2 style
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_session():
    """FastAPI dependency to provide a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
