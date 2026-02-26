"""Persisted event bus with a versioned envelope schema."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Mapping
from uuid import uuid4

from aivp.runtime.db import bootstrap_sqlite

EVENT_ENVELOPE_VERSION = "v1"

ACK_PENDING = "pending"
ACK_ACKED = "acked"
ACK_NACKED = "nacked"

AckState = Literal["pending", "acked", "nacked"]
TerminalAckState = Literal["acked", "nacked"]

EVENTS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS bus_events (
    event_id TEXT PRIMARY KEY,
    envelope_version TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_source TEXT NOT NULL,
    correlation_id TEXT,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    persisted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ack_state TEXT NOT NULL DEFAULT 'pending'
        CHECK (ack_state IN ('pending', 'acked', 'nacked')),
    acked_at TEXT
)
"""

EVENTS_TABLE_PENDING_IDX_DDL = """
CREATE INDEX IF NOT EXISTS idx_bus_events_ack_state_created_at
ON bus_events (ack_state, created_at, event_id)
"""


class DuplicateEventError(ValueError):
    """Raised when an event with the same event_id already exists."""


class InvalidAckStateError(ValueError):
    """Raised when ack state is unsupported for an operation."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class EventEnvelope:
    """Versioned event envelope persisted in the local event bus."""

    event_type: str
    event_source: str
    payload: Mapping[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid4()))
    envelope_version: str = EVENT_ENVELOPE_VERSION
    created_at: str = field(default_factory=_utc_now_iso)
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id must be non-empty")
        if not self.event_type.strip():
            raise ValueError("event_type must be non-empty")
        if not self.event_source.strip():
            raise ValueError("event_source must be non-empty")
        if not self.envelope_version.strip():
            raise ValueError("envelope_version must be non-empty")


@dataclass(frozen=True)
class PersistedEvent:
    """Event row materialized from SQLite storage."""

    event_id: str
    envelope_version: str
    event_type: str
    event_source: str
    payload: dict[str, Any]
    correlation_id: str | None
    created_at: str
    persisted_at: str
    ack_state: AckState
    acked_at: str | None


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_bus_tables(conn: sqlite3.Connection) -> None:
    conn.execute(EVENTS_TABLE_DDL)
    conn.execute(EVENTS_TABLE_PENDING_IDX_DDL)


def _row_to_persisted_event(row: sqlite3.Row) -> PersistedEvent:
    return PersistedEvent(
        event_id=str(row["event_id"]),
        envelope_version=str(row["envelope_version"]),
        event_type=str(row["event_type"]),
        event_source=str(row["event_source"]),
        payload=dict(json.loads(str(row["payload_json"]))),
        correlation_id=None
        if row["correlation_id"] is None
        else str(row["correlation_id"]),
        created_at=str(row["created_at"]),
        persisted_at=str(row["persisted_at"]),
        ack_state=str(row["ack_state"]),  # type: ignore[arg-type]
        acked_at=None if row["acked_at"] is None else str(row["acked_at"]),
    )


def _serialize_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _validate_terminal_ack_state(ack_state: str) -> None:
    if ack_state not in {ACK_ACKED, ACK_NACKED}:
        raise InvalidAckStateError(
            f"ack_state must be one of {ACK_ACKED!r}, {ACK_NACKED!r}"
        )


class SqliteEventBus:
    """SQLite-backed event bus with durable event persistence and ack state."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        bootstrap_sqlite(self.db_path)
        with _connect(self.db_path) as conn:
            _ensure_bus_tables(conn)
            conn.commit()

    def publish(self, envelope: EventEnvelope) -> PersistedEvent:
        """Persist an event envelope with initial pending ack state."""
        with _connect(self.db_path) as conn:
            _ensure_bus_tables(conn)
            try:
                conn.execute(
                    """
                    INSERT INTO bus_events (
                        event_id,
                        envelope_version,
                        event_type,
                        event_source,
                        correlation_id,
                        payload_json,
                        created_at,
                        ack_state
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        envelope.event_id,
                        envelope.envelope_version,
                        envelope.event_type,
                        envelope.event_source,
                        envelope.correlation_id,
                        _serialize_payload(envelope.payload),
                        envelope.created_at,
                        ACK_PENDING,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                if "UNIQUE constraint failed: bus_events.event_id" in str(exc):
                    raise DuplicateEventError(
                        f"event_id already exists: {envelope.event_id}"
                    ) from exc
                raise

            row = conn.execute(
                """
                SELECT
                    event_id,
                    envelope_version,
                    event_type,
                    event_source,
                    correlation_id,
                    payload_json,
                    created_at,
                    persisted_at,
                    ack_state,
                    acked_at
                FROM bus_events
                WHERE event_id = ?
                """,
                (envelope.event_id,),
            ).fetchone()
            conn.commit()

        if row is None:
            raise RuntimeError("published event could not be read back from storage")
        return _row_to_persisted_event(row)

    def get_event(self, event_id: str) -> PersistedEvent | None:
        with _connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT
                    event_id,
                    envelope_version,
                    event_type,
                    event_source,
                    correlation_id,
                    payload_json,
                    created_at,
                    persisted_at,
                    ack_state,
                    acked_at
                FROM bus_events
                WHERE event_id = ?
                """,
                (event_id,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_persisted_event(row)

    def list_pending(self, limit: int = 100) -> list[PersistedEvent]:
        if limit <= 0:
            return []
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT
                    event_id,
                    envelope_version,
                    event_type,
                    event_source,
                    correlation_id,
                    payload_json,
                    created_at,
                    persisted_at,
                    ack_state,
                    acked_at
                FROM bus_events
                WHERE ack_state = ?
                ORDER BY created_at ASC, event_id ASC
                LIMIT ?
                """,
                (ACK_PENDING, limit),
            ).fetchall()
        return [_row_to_persisted_event(row) for row in rows]

    def acknowledge(
        self, event_id: str, ack_state: TerminalAckState = ACK_ACKED
    ) -> bool:
        """Move a pending event to terminal acked/nacked state.

        Returns True when transition was applied or already in target state.
        Returns False when event does not exist.
        """
        _validate_terminal_ack_state(ack_state)

        with _connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE bus_events
                SET ack_state = ?, acked_at = CURRENT_TIMESTAMP
                WHERE event_id = ? AND ack_state = ?
                """,
                (ack_state, event_id, ACK_PENDING),
            )
            if cursor.rowcount and cursor.rowcount > 0:
                conn.commit()
                return True

            row = conn.execute(
                "SELECT ack_state FROM bus_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            conn.commit()

        if row is None:
            return False
        return str(row["ack_state"]) == ack_state
