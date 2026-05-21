from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

import pymssql


DB_HOST = os.getenv("DB_HOST", "database")
DB_PORT = int(os.getenv("DB_PORT", "1433"))
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MSSQL_SA_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME") or os.getenv("MSSQL_DATABASE", "NongNghiepAI")
INIT_SQL_FILE = Path(os.getenv("DB_INIT_SQL_FILE", "/app/NongNghiepAI_Full.sql"))
FORCE_DB_INIT = os.getenv("FORCE_DB_INIT", "false").strip().lower() in {"1", "true", "yes", "on"}
CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "90"))
CONNECT_DELAY_SECONDS = float(os.getenv("DB_CONNECT_DELAY_SECONDS", "2"))


def connect(database: str = "master"):
    return pymssql.connect(
        server=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database,
        login_timeout=5,
        timeout=120,
        charset="UTF-8",
        autocommit=True,
    )


def wait_for_sql_server() -> None:
    if not DB_PASSWORD:
        raise RuntimeError("DB_PASSWORD/MSSQL_SA_PASSWORD is required for SQL Server initialization.")

    last_error: Exception | None = None
    for attempt in range(1, CONNECT_RETRIES + 1):
        try:
            with connect("master") as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            print(f"[db-init] SQL Server is ready at {DB_HOST}:{DB_PORT}")
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f"[db-init] Waiting for SQL Server ({attempt}/{CONNECT_RETRIES}): {exc}")
            time.sleep(CONNECT_DELAY_SECONDS)
    raise RuntimeError(f"SQL Server did not become ready: {last_error}")


def database_exists() -> bool:
    with connect("master") as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DB_ID(%s)", (DB_NAME,))
            return cursor.fetchone()[0] is not None


def table_count() -> int:
    if not database_exists():
        return 0
    with connect(DB_NAME) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE is_ms_shipped = 0")
            return int(cursor.fetchone()[0])


def required_schema_exists() -> bool:
    if not database_exists():
        return False
    required_tables = ("Users", "CropTypes", "MarketPrices", "PriceHistory")
    with connect(DB_NAME) as conn:
        with conn.cursor() as cursor:
            placeholders = ",".join(["%s"] * len(required_tables))
            cursor.execute(
                f"SELECT COUNT(*) FROM sys.tables WHERE name IN ({placeholders})",
                required_tables,
            )
            return int(cursor.fetchone()[0]) == len(required_tables)


def init_marker_exists() -> bool:
    if not database_exists():
        return False
    with connect(DB_NAME) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                IF OBJECT_ID('DockerSchemaMigrations', 'U') IS NULL
                    SELECT 0
                ELSE
                    SELECT COUNT(*) FROM DockerSchemaMigrations
                    WHERE InitName = %s
                """,
                (INIT_SQL_FILE.name,),
            )
            return int(cursor.fetchone()[0]) > 0


def write_init_marker() -> None:
    with connect(DB_NAME) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                IF OBJECT_ID('DockerSchemaMigrations', 'U') IS NULL
                BEGIN
                    CREATE TABLE DockerSchemaMigrations (
                        InitName NVARCHAR(255) NOT NULL PRIMARY KEY,
                        AppliedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
                    )
                END
                MERGE DockerSchemaMigrations AS target
                USING (SELECT %s AS InitName) AS source
                ON target.InitName = source.InitName
                WHEN MATCHED THEN UPDATE SET AppliedAt = SYSUTCDATETIME()
                WHEN NOT MATCHED THEN INSERT (InitName) VALUES (source.InitName);
                """,
                (INIT_SQL_FILE.name,),
            )


def split_sql_batches(sql: str) -> list[str]:
    batches: list[str] = []
    current: list[str] = []
    go_pattern = re.compile(r"^\s*GO\s*(?:--.*)?$", re.IGNORECASE)

    for line in sql.splitlines():
        if go_pattern.match(line):
            batch = "\n".join(current).strip()
            if batch:
                batches.append(batch)
            current = []
        else:
            current.append(line)

    tail = "\n".join(current).strip()
    if tail:
        batches.append(tail)
    return batches


def execute_sql_file() -> None:
    if not INIT_SQL_FILE.exists():
        print(f"[db-init] {INIT_SQL_FILE} not found; creating empty database {DB_NAME}.")
        quoted_db_name = DB_NAME.replace("]", "]]")
        with connect("master") as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"IF DB_ID(%s) IS NULL CREATE DATABASE [{quoted_db_name}]", (DB_NAME,))
        return

    sql = INIT_SQL_FILE.read_text(encoding="utf-8-sig")
    batches = split_sql_batches(sql)
    print(f"[db-init] Executing {INIT_SQL_FILE.name} ({len(batches)} batches)")

    with connect("master") as conn:
        with conn.cursor() as cursor:
            for index, batch in enumerate(batches, start=1):
                try:
                    cursor.execute(batch)
                    while cursor.nextset():
                        pass
                except Exception as exc:  # noqa: BLE001
                    preview = " ".join(batch.split())[:500]
                    raise RuntimeError(f"Batch {index}/{len(batches)} failed: {preview}") from exc


def main() -> int:
    wait_for_sql_server()

    existing_tables = table_count()
    has_required_schema = required_schema_exists()
    has_marker = init_marker_exists()
    if existing_tables and has_required_schema and not FORCE_DB_INIT:
        if not has_marker:
            write_init_marker()
        print(f"[db-init] Database {DB_NAME} already has required tables; skipping init.")
        return 0

    if existing_tables and FORCE_DB_INIT:
        print(f"[db-init] FORCE_DB_INIT=true; reinitializing {DB_NAME}.")
    elif existing_tables:
        print(f"[db-init] Database {DB_NAME} has {existing_tables} tables but schema is incomplete; reinitializing.")
    else:
        print(f"[db-init] Initializing database {DB_NAME}.")

    execute_sql_file()
    write_init_marker()
    print(f"[db-init] Database {DB_NAME} is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
