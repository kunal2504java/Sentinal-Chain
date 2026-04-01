"""SQLite-backed retry queue for failed blockchain submissions."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.detector import Event
    from chain.contract import AvalancheLogger


def _utc_now() -> str:
    """Return the current UTC timestamp as ISO-8601."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _serialize_event(event: Any) -> str:
    """Serialize an event-like object to JSON for queue storage."""
    if is_dataclass(event):
        payload = asdict(event)
    elif isinstance(event, dict):
        payload = dict(event)
    else:
        payload = {
            "type": getattr(event, "type"),
            "confidence": getattr(event, "confidence"),
            "timestamp": getattr(event, "timestamp"),
            "camera_id": getattr(event, "camera_id"),
        }

    payload.pop("frame_snapshot", None)
    return json.dumps(payload)


class PendingEventQueue:
    """Persist failed blockchain submissions for later retry."""

    def __init__(self, sqlite_path: str = "./sentinelchain.db") -> None:
        """Initialize the pending event queue."""
        self.sqlite_path = Path(sqlite_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """Create a SQLite connection."""
        return sqlite3.connect(self.sqlite_path)

    def _initialize(self) -> None:
        """Create the pending events table if it does not exist."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_json TEXT NOT NULL,
                    clip_hash TEXT NOT NULL,
                    ipfs_cid TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_attempt TEXT,
                    next_attempt_at TEXT,
                    tx_hash TEXT,
                    submitted_at TEXT,
                    failed_at TEXT
                )
                """
            )

    def add_to_queue(self, event: Event | dict[str, Any], clip_hash: str, ipfs_cid: str) -> int:
        """Insert a failed submission into the retry queue."""
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO pending_events (
                    event_json,
                    clip_hash,
                    ipfs_cid,
                    created_at,
                    attempts,
                    last_attempt,
                    next_attempt_at
                ) VALUES (?, ?, ?, ?, 0, NULL, ?)
                """,
                (_serialize_event(event), clip_hash, ipfs_cid, _utc_now(), _utc_now()),
            )
            return int(cursor.lastrowid)

    def get_pending(self) -> list[dict[str, Any]]:
        """Return all queue records that have not been submitted."""
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, event_json, clip_hash, ipfs_cid, created_at, attempts, last_attempt, next_attempt_at
                FROM pending_events
                WHERE tx_hash IS NULL AND failed_at IS NULL
                ORDER BY created_at ASC
                """
            ).fetchall()

        pending: list[dict[str, Any]] = []
        for row in rows:
            record = dict(row)
            record["event"] = json.loads(record.pop("event_json"))
            pending.append(record)
        return pending

    def _retry_delay_seconds(self, attempts: int) -> int:
        """Return the next retry delay based on exponential backoff."""
        schedule = [30, 60, 120, 300]
        if attempts < len(schedule):
            return schedule[attempts]
        return 300

    def increment_attempts(self, queue_id: int, attempts: int) -> None:
        """Increment the retry attempt counter for a queued event."""
        now = datetime.now(timezone.utc)
        next_attempt = now.timestamp() + self._retry_delay_seconds(attempts)
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE pending_events
                SET attempts = attempts + 1,
                    last_attempt = ?,
                    next_attempt_at = ?
                WHERE id = ?
                """,
                (
                    now.isoformat().replace("+00:00", "Z"),
                    datetime.fromtimestamp(next_attempt, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                    queue_id,
                ),
            )

    def mark_failed(self, queue_id: int) -> None:
        """Mark a queued event as permanently failed."""
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE pending_events
                SET failed_at = ?,
                    last_attempt = ?
                WHERE id = ?
                """,
                (_utc_now(), _utc_now(), queue_id),
            )

    def mark_submitted(self, queue_id: int, tx_hash: str) -> None:
        """Mark a queued event as successfully submitted on-chain."""
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE pending_events
                SET tx_hash = ?,
                    submitted_at = ?,
                    last_attempt = ?
                WHERE id = ?
                """,
                (tx_hash, _utc_now(), _utc_now(), queue_id),
            )

    def retry_pending(self, logger: AvalancheLogger) -> list[str]:
        """Retry all pending blockchain submissions and return successful tx hashes."""
        submitted_hashes: list[str] = []
        now = datetime.now(timezone.utc)
        for record in self.get_pending():
            next_attempt_at = record.get("next_attempt_at")
            if next_attempt_at:
                scheduled = datetime.fromisoformat(next_attempt_at.replace("Z", "+00:00"))
                if scheduled > now:
                    continue
            if int(record["attempts"]) >= 20:
                self.mark_failed(record["id"])
                continue
            self.increment_attempts(record["id"], int(record["attempts"]))
            try:
                tx_hash = logger.submit_queued_event(
                    event_payload=record["event"],
                    clip_hash=record["clip_hash"],
                    ipfs_cid=record["ipfs_cid"],
                )
            except Exception:
                continue
            self.mark_submitted(record["id"], tx_hash)
            submitted_hashes.append(tx_hash)
        return submitted_hashes
