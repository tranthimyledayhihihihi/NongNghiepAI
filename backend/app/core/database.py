from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


SQLITE_FALLBACK_URL = "sqlite:///./agri_ai.db"


def _connect_args(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _build_engine(database_url: str):
    return create_engine(
        database_url,
        connect_args=_connect_args(database_url),
        pool_pre_ping=not database_url.startswith("sqlite"),
    )


def _create_configured_engine():
    try:
        return _build_engine(settings.DATABASE_URL), settings.DATABASE_URL
    except (ImportError, ModuleNotFoundError):
        if settings.ENVIRONMENT.lower() == "production":
            raise
        return _build_engine(SQLITE_FALLBACK_URL), SQLITE_FALLBACK_URL


engine, active_database_url = _create_configured_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _switch_to_sqlite_fallback():
    global engine, active_database_url
    engine = _build_engine(SQLITE_FALLBACK_URL)
    active_database_url = SQLITE_FALLBACK_URL
    SessionLocal.configure(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create database tables for the imported SQLAlchemy models."""
    import app.models  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError:
        if settings.ENVIRONMENT.lower() == "production" or active_database_url.startswith("sqlite"):
            raise
        _switch_to_sqlite_fallback()
        Base.metadata.create_all(bind=engine)
