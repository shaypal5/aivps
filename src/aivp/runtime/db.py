"""SQLite bootstrap and migration-version helpers."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

SCHEMA_STATE_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS schema_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    migration_version TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


@dataclass(frozen=True)
class DbBootstrapResult:
    db_path: str
    migration_version: str
    journal_mode: str
    wal_enabled: bool
    created_state_row: bool


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def _normalize_journal_mode(mode: str) -> str:
    return mode.strip().lower()


def _ensure_schema_state_table(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA_STATE_TABLE_DDL)


def bootstrap_sqlite(
    db_path: Path,
    initial_migration_version: str = "v1alpha1",
) -> DbBootstrapResult:
    """Initialize SQLite runtime DB, WAL mode, and migration state table."""
    with _connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")

        _ensure_schema_state_table(conn)

        created_state_row = False
        cursor = conn.execute(
            """
            INSERT INTO schema_state (id, migration_version)
            VALUES (1, ?)
            ON CONFLICT(id) DO NOTHING
            """,
            (initial_migration_version,),
        )
        if cursor.rowcount and cursor.rowcount > 0:
            created_state_row = True

        row = conn.execute(
            "SELECT migration_version FROM schema_state WHERE id = 1"
        ).fetchone()
        migration_version = (
            initial_migration_version if row is None else str(row[0])
        )

        journal_mode_row = conn.execute("PRAGMA journal_mode").fetchone()
        journal_mode = (
            _normalize_journal_mode(str(journal_mode_row[0]))
            if journal_mode_row
            else "unknown"
        )

        conn.commit()

    return DbBootstrapResult(
        db_path=str(db_path),
        migration_version=migration_version,
        journal_mode=journal_mode,
        wal_enabled=journal_mode == "wal",
        created_state_row=created_state_row,
    )


def get_migration_version(db_path: Path) -> str | None:
    if not db_path.exists():
        return None

    with _connect(db_path) as conn:
        try:
            row = conn.execute(
                "SELECT migration_version FROM schema_state WHERE id = 1"
            ).fetchone()
        except sqlite3.OperationalError as exc:
            if "no such table: schema_state" in str(exc):
                return None
            raise

        if row is None:
            return None
        return str(row[0])


def set_migration_version(db_path: Path, migration_version: str) -> None:
    with _connect(db_path) as conn:
        _ensure_schema_state_table(conn)
        conn.execute(
            """
            INSERT INTO schema_state (id, migration_version)
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET
                migration_version = excluded.migration_version,
                updated_at = CURRENT_TIMESTAMP
            """,
            (migration_version,),
        )
        conn.commit()
