from sqlalchemy import create_engine, text
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


def _is_sqlite() -> bool:
    return active_database_url.startswith("sqlite")


def _quote_sqlite_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _sqlite_table_name(conn, table_name: str) -> str | None:
    return conn.execute(
        text(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND lower(name) = lower(:table_name)"
        ),
        {"table_name": table_name},
    ).scalar()


def _sqlite_columns(conn, table_name: str) -> set[str]:
    quoted_table = _quote_sqlite_identifier(table_name)
    rows = conn.exec_driver_sql(f"PRAGMA table_info({quoted_table})").fetchall()
    return {row[1] for row in rows}


def _sqlite_rename_table(conn, source_table: str, target_table: str) -> str:
    legacy_table = target_table
    suffix = 1
    while _sqlite_table_name(conn, legacy_table):
        suffix += 1
        legacy_table = f"{target_table}_{suffix}"
    conn.exec_driver_sql(
        "ALTER TABLE "
        f"{_quote_sqlite_identifier(source_table)} "
        f"RENAME TO {_quote_sqlite_identifier(legacy_table)}"
    )
    return legacy_table


def _migrate_legacy_sqlite_users() -> str | None:
    """Move the old lowercase users table out of the way before create_all().

    Older local databases used a lowercase `users` table with columns like
    `id` and `full_name`. SQLite resolves table names case-insensitively, so
    that table prevents SQLAlchemy from creating the current `Users` table.
    """
    if not _is_sqlite():
        return None

    with engine.begin() as conn:
        users_table = _sqlite_table_name(conn, "Users")
        if not users_table:
            return None
        if "UserID" in _sqlite_columns(conn, users_table):
            return None
        return _sqlite_rename_table(conn, users_table, "legacy_users")


def _copy_legacy_sqlite_users(legacy_table: str | None) -> None:
    if not legacy_table or not _is_sqlite():
        return

    with engine.begin() as conn:
        if not _sqlite_table_name(conn, "Users"):
            return
        legacy_columns = _sqlite_columns(conn, legacy_table)
        if not {"id", "full_name", "password_hash"}.issubset(legacy_columns):
            return

        quoted_legacy = _quote_sqlite_identifier(legacy_table)
        conn.exec_driver_sql(
            f"""
            INSERT OR IGNORE INTO "Users"
                ("UserID", "FullName", "Email", "PhoneNumber", "ZaloID",
                 "PasswordHash", "Role", "Region", "IsActive", "IsVerified",
                 "CreatedAt", "UpdatedAt")
            SELECT
                id,
                full_name,
                email,
                phone_number,
                zalo_id,
                password_hash,
                COALESCE(role, 'farmer'),
                region,
                COALESCE(is_active, 1),
                COALESCE(is_verified, 0),
                COALESCE(created_at, CURRENT_TIMESTAMP),
                COALESCE(updated_at, CURRENT_TIMESTAMP)
            FROM {quoted_legacy}
            """
        )


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
    from app.core.seed import seed_demo_users

    try:
        legacy_users_table = _migrate_legacy_sqlite_users()
        Base.metadata.create_all(bind=engine)
        _copy_legacy_sqlite_users(legacy_users_table)
        seed_demo_users(SessionLocal)
    except SQLAlchemyError:
        if settings.ENVIRONMENT.lower() == "production" or active_database_url.startswith("sqlite"):
            raise
        _switch_to_sqlite_fallback()
        legacy_users_table = _migrate_legacy_sqlite_users()
        Base.metadata.create_all(bind=engine)
        _copy_legacy_sqlite_users(legacy_users_table)
        seed_demo_users(SessionLocal)
