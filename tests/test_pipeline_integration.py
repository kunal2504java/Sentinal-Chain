"""Integration test for the event pipeline with mocked services."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sqlite3

import numpy as np
import pytest

from config import load_settings
from core.detector import Event
import pipeline

cv2 = pytest.importorskip("cv2")
from pipeline import run_pipeline


class FakeCapture:
    """A fake video capture that yields a bounded list of frames."""

    def __init__(self, frames: list[np.ndarray]) -> None:
        """Initialize the fake capture."""
        self.frames = frames
        self.index = 0
        self.opened = True

    def isOpened(self) -> bool:
        """Return whether the capture is open."""
        return self.opened

    def read(self) -> tuple[bool, np.ndarray | None]:
        """Return the next frame or stop the pipeline."""
        if self.index >= len(self.frames):
            self.opened = False
            raise KeyboardInterrupt
        frame = self.frames[self.index]
        self.index += 1
        return True, frame

    def get(self, prop_id: int) -> float:
        """Return a fake FPS value."""
        if prop_id == cv2.CAP_PROP_FPS:
            return 10.0
        return 0.0

    def release(self) -> None:
        """Release the fake capture."""
        self.opened = False


class FakeDetector:
    """Emit a single event after a fixed number of frames."""

    def __init__(self, trigger_at: int = 4) -> None:
        """Initialize the fake detector."""
        self.trigger_at = trigger_at
        self.calls = 0

    def detect(self, frame: np.ndarray, camera_id: str, timestamp=None) -> Event | None:
        """Return a mock event when the trigger threshold is reached."""
        self.calls += 1
        if self.calls != self.trigger_at:
            return None
        return Event(
            type="fire_smoke",
            confidence=0.93,
            timestamp=timestamp.isoformat().replace("+00:00", "Z"),
            frame_snapshot=frame.copy(),
            camera_id=camera_id,
        )


class FakePinataClient:
    """Mock Pinata uploads."""

    def upload_clip(self, filepath: str, metadata: dict[str, str]) -> str:
        """Return a fake CID."""
        return "bafy-test-cid"

    def verify_upload(self, cid: str) -> bool:
        """Always accept the uploaded CID."""
        return True

    def get_ipfs_url(self, cid: str) -> str:
        """Return a fake gateway URL."""
        return f"https://gateway.pinata.cloud/ipfs/{cid}"


class FakeTelegramAlerter:
    """Mock Telegram delivery."""

    async def send_event_alert(self, event: Event, tx_hash: str, ipfs_url: str, clip_path: str) -> None:
        """No-op mocked alert."""
        return None


class FakeQueue:
    """Mock retry queue."""

    def retry_pending(self, logger) -> list[str]:
        """Return no retried items."""
        return []


class FakeAvalancheLogger:
    """Mock Avalanche submission."""

    def __init__(self) -> None:
        """Initialize the fake logger."""
        self.queue = FakeQueue()

    def log_event(self, event: Event, clip_hash: str, ipfs_cid: str) -> str:
        """Return a fake transaction hash."""
        return "0xabc123"

    def get_explorer_url(self, tx_hash: str) -> str:
        """Return a fake explorer URL."""
        return f"https://testnet.snowtrace.io/tx/{tx_hash}"


def test_pipeline_integration(tmp_path, monkeypatch) -> None:
    """Run the pipeline end-to-end with mocked chain and IPFS services."""
    sqlite_path = tmp_path / "sentinelchain.db"
    events_dir = tmp_path / "events"
    monkeypatch.setenv("SQLITE_PATH", str(sqlite_path))

    frames = [np.full((32, 32, 3), fill_value=index * 20, dtype=np.uint8) for index in range(6)]
    capture = FakeCapture(frames)
    detector = FakeDetector(trigger_at=4)
    monotonic_state = {"value": 0.0}

    def fake_monotonic() -> float:
        monotonic_state["value"] += 1.0
        return monotonic_state["value"]

    monkeypatch.setattr(pipeline.time, "monotonic", fake_monotonic)

    settings = replace(
        load_settings(),
        camera_source="tests/fixtures/sample_fire.mp4",
        camera_id="CAM_TEST",
        events_dir=events_dir,
        process_fps=100000,
        retry_interval_seconds=60,
        reconnect_interval_seconds=1,
    )

    run_pipeline(
        settings=settings,
        detector=detector,
        pinata_client=FakePinataClient(),
        avalanche_logger=FakeAvalancheLogger(),
        telegram_alerter=FakeTelegramAlerter(),
        capture_factory=lambda source: capture,
    )

    with sqlite3.connect(sqlite_path) as connection:
        row = connection.execute(
            "SELECT event_type, camera_id, ipfs_cid, tx_hash, clip_path FROM events"
        ).fetchone()

    assert row is not None
    assert row[0] == "fire_smoke"
    assert row[1] == "CAM_TEST"
    assert row[2] == "bafy-test-cid"
    assert row[3] == "0xabc123"
    assert Path(row[4]).exists()
