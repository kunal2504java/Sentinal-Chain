"""FastAPI endpoints for SentinelChain event records."""

from __future__ import annotations

from io import BytesIO
import json
import os
from pathlib import Path
import sqlite3
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from chain.contract import AvalancheLogger
from core.hasher import hash_file


SQLITE_PATH = Path(os.getenv("SQLITE_PATH", "./sentinelchain.db"))

app = FastAPI(title="SentinelChain API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _connect() -> sqlite3.Connection:
    """Create a SQLite connection with row mapping support."""
    connection = sqlite3.connect(SQLITE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _get_event(event_id: int) -> dict[str, Any]:
    """Load a single event record from SQLite."""
    with _connect() as connection:
        row = connection.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    return dict(row)


def _safe_on_chain_hash(event_id: int) -> str | None:
    """Fetch an on-chain hash when chain access is configured and available."""
    try:
        logger = AvalancheLogger()
        payload = logger.verify_event(event_id)
        return str(payload["clipHash"])
    except Exception:
        return None


def _integrity_snapshot(event: dict[str, Any]) -> tuple[str | None, str | None, bool | None]:
    """Return local hash, on-chain hash, and whether they match."""
    clip_path = Path(event["clip_path"])
    local_hash = hash_file(str(clip_path)) if clip_path.exists() else None
    on_chain_hash = _safe_on_chain_hash(int(event["id"]))
    if local_hash is None or on_chain_hash is None:
        return local_hash, on_chain_hash, None
    return local_hash, on_chain_hash, local_hash == on_chain_hash


@app.get("/health")
def health() -> dict[str, str]:
    """Return a basic health response."""
    return {"status": "ok"}


@app.get("/api/events")
def list_events(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)) -> list[dict[str, Any]]:
    """List event records with pagination support."""
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM events
            ORDER BY datetime(timestamp) DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/events/{event_id}")
def event_detail(event_id: int) -> dict[str, Any]:
    """Return a single event record."""
    return _get_event(event_id)


@app.get("/api/events/{event_id}/verify")
def verify_event(event_id: int) -> dict[str, Any]:
    """Re-hash a clip and compare it against the on-chain record."""
    event = _get_event(event_id)
    local_hash, on_chain_hash, match = _integrity_snapshot(event)
    if local_hash is None:
        raise HTTPException(status_code=404, detail="Clip file not found.")
    return {
        "match": bool(match),
        "on_chain_hash": on_chain_hash,
        "local_hash": local_hash,
    }


@app.get("/api/stats")
def stats() -> dict[str, Any]:
    """Return aggregate event statistics."""
    with _connect() as connection:
        total_events = int(connection.execute("SELECT COUNT(*) FROM events").fetchone()[0])
        events_today = int(
            connection.execute(
                "SELECT COUNT(*) FROM events WHERE date(timestamp) = date('now')"
            ).fetchone()[0]
        )
        rows = connection.execute("SELECT * FROM events").fetchall()

    verified = 0
    for row in rows:
        _, _, match = _integrity_snapshot(dict(row))
        if match:
            verified += 1

    integrity_rate = (verified / total_events * 100) if total_events else 0.0
    return {
        "total_events": total_events,
        "events_today": events_today,
        "integrity_rate": round(integrity_rate, 2),
    }


@app.post("/api/events/{event_id}/export")
def export_event(event_id: int) -> StreamingResponse:
    """Export a zip package with the clip, manifest, and proof text."""
    event = _get_event(event_id)
    clip_path = Path(event["clip_path"])
    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip file not found.")

    local_hash, on_chain_hash, match = _integrity_snapshot(event)
    manifest = {
        "id": event["id"],
        "eventType": event["event_type"],
        "cameraId": event["camera_id"],
        "timestamp": event["timestamp"],
        "clipPath": event["clip_path"],
        "clipHash": event["clip_hash"],
        "localHash": local_hash,
        "ipfsCid": event["ipfs_cid"],
        "txHash": event["tx_hash"],
        "confidence": event["confidence"],
        "integrityMatch": match,
    }
    proof = "\n".join(
        [
            f"Event ID: {event['id']}",
            f"Avalanche TX: {event['tx_hash']}",
            f"IPFS CID: {event['ipfs_cid']}",
            f"Stored hash: {event['clip_hash']}",
            f"On-chain hash: {on_chain_hash or 'Unavailable'}",
            f"Local hash: {local_hash or 'Unavailable'}",
            "",
            "Verification instructions:",
            "1. Compute the SHA-256 hash of the clip file.",
            "2. Compare it with manifest.json and the Avalanche record.",
            "3. Confirm the IPFS CID and transaction details match.",
        ]
    )

    archive = BytesIO()
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.write(clip_path, arcname=clip_path.name)
        zip_file.writestr("manifest.json", json.dumps(manifest, indent=2))
        zip_file.writestr("proof.txt", proof)
    archive.seek(0)

    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="event-{event_id}.zip"'},
    )
