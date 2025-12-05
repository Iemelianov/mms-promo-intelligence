"""
Database session utilities.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoSuchModuleError

from db.base import ensure_metadata_column, Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mms.db")

# Use future engine for SQLAlchemy 2 style
engine = create_engine(DATABASE_URL, future=True)

# Backward-compatibility migration: rename legacy 'metadata' column if present.
ensure_metadata_column(engine)

# Ensure tables exist (best-effort for dev/local environments).
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_session():
    """FastAPI dependency to provide a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
