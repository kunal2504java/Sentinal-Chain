"""Main entry point for the hardened detection pipeline."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import logging
import os
import sqlite3
import time
from typing import Any

import cv2

from alerts.telegram import TelegramAlerter
from chain.contract import AvalancheLogger
from chain.ipfs import PinataClient
from config import Settings, load_settings
from core.buffer import RollingBuffer
from core.clipper import ClipWriter
from core.detector import Detector, Event
from core.hasher import hash_file


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the SentinelChain detection pipeline.")
    parser.add_argument("--source", help="Override CAMERA_SOURCE with a camera index or RTSP/file path.")
    parser.add_argument("--fps", type=int, help="Limit processing rate in frames per second.")
    return parser.parse_args()


def _configure_logging(level: str) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _initialize_events_table(sqlite_path: str) -> None:
    """Create the SQLite tables used by the pipeline if they do not exist."""
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                camera_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                clip_path TEXT NOT NULL,
                clip_hash TEXT NOT NULL,
                ipfs_cid TEXT NOT NULL,
                tx_hash TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def _persist_event_record(
    sqlite_path: str,
    event_type: str,
    camera_id: str,
    timestamp: str,
    clip_path: str,
    clip_hash: str,
    ipfs_cid: str,
    tx_hash: str,
    confidence: float,
) -> None:
    """Persist a complete event record to SQLite."""
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            """
            INSERT INTO events (
                event_type,
                camera_id,
                timestamp,
                clip_path,
                clip_hash,
                ipfs_cid,
                tx_hash,
                confidence,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_type,
                camera_id,
                timestamp,
                clip_path,
                clip_hash,
                ipfs_cid,
                tx_hash,
                confidence,
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            ),
        )


def _persist_system_event(sqlite_path: str, event_type: str, message: str) -> None:
    """Persist a pipeline system event to SQLite."""
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            """
            INSERT INTO system_events (event_type, message, created_at)
            VALUES (?, ?, ?)
            """,
            (
                event_type,
                message,
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            ),
        )


def _build_capture(source: int | str) -> cv2.VideoCapture:
    """Create a capture object for a source."""
    return cv2.VideoCapture(source)


def _handle_event(
    *,
    event: Event,
    buffer: RollingBuffer,
    clip_writer: ClipWriter,
    settings: Settings,
    sqlite_path: str,
    pinata_client: PinataClient,
    avalanche_logger: AvalancheLogger | None,
    telegram_alerter: TelegramAlerter,
    logger: logging.Logger,
) -> None:
    """Process a confirmed event end-to-end."""
    clip_frames = buffer.get_clip(
        seconds_before=settings.clip_before_seconds,
        seconds_after=settings.clip_after_seconds,
        event_timestamp=event.timestamp,
    )
    clip_path = clip_writer.write_clip(
        frames=clip_frames,
        event_type=event.type,
        event_timestamp=event.timestamp,
    )
    clip_hash = hash_file(clip_path)
    metadata = {
        "event_type": event.type,
        "timestamp": event.timestamp,
        "camera_id": event.camera_id,
    }

    ipfs_cid = "local-only"
    try:
        ipfs_cid = pinata_client.upload_clip(clip_path, metadata)
        if not pinata_client.verify_upload(ipfs_cid):
            raise RuntimeError(f"Uploaded CID is not reachable: {ipfs_cid}")
    except Exception as exc:
        logger.warning("IPFS upload failed for %s: %s", clip_path, exc)

    tx_hash = "not-submitted"
    explorer_url = tx_hash
    if avalanche_logger is not None:
        try:
            tx_hash = avalanche_logger.log_event(event=event, clip_hash=clip_hash, ipfs_cid=ipfs_cid)
            explorer_url = (
                avalanche_logger.get_explorer_url(tx_hash)
                if not tx_hash.startswith("queued:")
                else tx_hash
            )
        except Exception as exc:
            logger.warning("Avalanche logging failed for %s: %s", clip_path, exc)

    ipfs_url = pinata_client.get_ipfs_url(ipfs_cid) if ipfs_cid != "local-only" else ipfs_cid
    try:
        asyncio.run(
            telegram_alerter.send_event_alert(
                event=event,
                tx_hash=explorer_url,
                ipfs_url=ipfs_url,
                clip_path=clip_path,
            )
        )
    except Exception as exc:
        logger.warning("Telegram alert failed for %s: %s", clip_path, exc)

    _persist_event_record(
        sqlite_path=sqlite_path,
        event_type=event.type,
        camera_id=event.camera_id,
        timestamp=event.timestamp,
        clip_path=clip_path,
        clip_hash=clip_hash,
        ipfs_cid=ipfs_cid,
        tx_hash=tx_hash,
        confidence=event.confidence,
    )
    logger.info(
        "Event detected: type=%s confidence=%.2f camera_id=%s clip=%s sha256=%s ipfs=%s tx=%s",
        event.type,
        event.confidence,
        event.camera_id,
        clip_path,
        clip_hash,
        ipfs_cid,
        tx_hash,
    )


def run_pipeline(
    *,
    settings: Settings,
    source_override: int | str | None = None,
    fps_override: int | None = None,
    detector: Detector | Any | None = None,
    pinata_client: PinataClient | Any | None = None,
    avalanche_logger: AvalancheLogger | Any | None = None,
    telegram_alerter: TelegramAlerter | Any | None = None,
    capture_factory=None,
) -> None:
    """Run the synchronous detection pipeline loop."""
    logger = logging.getLogger("pipeline")
    sqlite_path = os.getenv("SQLITE_PATH", "./sentinelchain.db")
    _initialize_events_table(sqlite_path)

    camera_source = source_override if source_override is not None else settings.camera_source
    capture_builder = capture_factory or _build_capture
    capture = capture_builder(camera_source)

    while not capture.isOpened():
        logger.warning(
            "Video source unavailable: %s. Retrying in %s seconds.",
            camera_source,
            settings.reconnect_interval_seconds,
        )
        _persist_system_event(sqlite_path, "camera_disconnect", f"Disconnected from source {camera_source}")
        time.sleep(settings.reconnect_interval_seconds)
        capture = capture_builder(camera_source)

    fps = capture.get(cv2.CAP_PROP_FPS) or float(settings.process_fps or 10)
    process_fps = float(fps_override or settings.process_fps or 10)
    min_frame_interval = 1.0 / max(process_fps, 1.0)
    last_processed_at = 0.0
    last_retry_at = 0.0

    buffer = RollingBuffer(fps=fps, buffer_seconds=settings.buffer_seconds)
    detector = detector or Detector(
        model_path=settings.model_path,
        confidence_threshold=settings.confidence_threshold,
        frame_confirmation_n=settings.frame_confirmation_n,
        frame_confirmation_m=settings.frame_confirmation_m,
        nms_iou_threshold=settings.nms_iou_threshold,
        min_bbox_area=settings.min_bbox_area,
        ignore_zones=settings.ignore_zones,
    )
    clip_writer = ClipWriter(events_dir=settings.events_dir, fps=fps)
    pinata_client = pinata_client or PinataClient()
    telegram_alerter = telegram_alerter or TelegramAlerter()

    if avalanche_logger is not None:
        try:
            avalanche_logger.queue.retry_pending(avalanche_logger)
        except Exception as exc:
            logger.warning("Initial queue retry failed: %s", exc)

    logger.info("Pipeline started for camera %s", settings.camera_id)

    try:
        while True:
            current_monotonic = time.monotonic()
            if avalanche_logger is not None and current_monotonic - last_retry_at >= settings.retry_interval_seconds:
                last_retry_at = current_monotonic
                try:
                    avalanche_logger.queue.retry_pending(avalanche_logger)
                except Exception as exc:
                    logger.warning("Pending queue retry failed: %s", exc)

            ok, frame = capture.read()
            if not ok:
                logger.warning("Video source ended or frame capture failed. Attempting reconnect.")
                _persist_system_event(sqlite_path, "camera_disconnect", f"Lost frames from source {camera_source}")
                capture.release()
                time.sleep(settings.reconnect_interval_seconds)
                capture = capture_builder(camera_source)
                if capture.isOpened():
                    _persist_system_event(sqlite_path, "camera_reconnect", f"Reconnected to source {camera_source}")
                continue

            if current_monotonic - last_processed_at < min_frame_interval:
                continue
            last_processed_at = current_monotonic

            frame_time = datetime.now(timezone.utc)
            buffer.push_frame(frame, frame_time)
            event = detector.detect(frame=frame, camera_id=settings.camera_id, timestamp=frame_time)
            if event is None:
                continue

            _handle_event(
                event=event,
                buffer=buffer,
                clip_writer=clip_writer,
                settings=settings,
                sqlite_path=sqlite_path,
                pinata_client=pinata_client,
                avalanche_logger=avalanche_logger,
                telegram_alerter=telegram_alerter,
                logger=logger,
            )
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user.")
    finally:
        capture.release()
        logger.info("Pipeline stopped.")


def main() -> None:
    """Run the synchronous detection pipeline loop."""
    args = _parse_args()
    settings = load_settings()
    if args.source is not None:
        settings.camera_source = int(args.source) if args.source.isdigit() else args.source

    _configure_logging(settings.log_level)
    avalanche_logger: AvalancheLogger | None = None
    try:
        avalanche_logger = AvalancheLogger(sqlite_path=os.getenv("SQLITE_PATH", "./sentinelchain.db"))
    except Exception as exc:
        logging.getLogger("pipeline").warning("Avalanche logger unavailable at startup: %s", exc)

    run_pipeline(
        settings=settings,
        source_override=args.source,
        fps_override=args.fps,
        avalanche_logger=avalanche_logger,
    )


if __name__ == "__main__":
    main()
