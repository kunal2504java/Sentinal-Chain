"""Tests for detection confirmation behavior."""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from core.detector import Detector, Event


class DummyModel:
    """Return a predefined sequence of predictions."""

    def __init__(self, predictions: list[list[dict[str, float | str]]]) -> None:
        """Initialize the dummy model."""
        self._predictions = predictions
        self._index = 0

    def predict(self, frame: np.ndarray, verbose: bool = False) -> list[dict[str, float | str]]:
        """Return the next prediction payload."""
        prediction = self._predictions[self._index]
        self._index += 1
        return prediction


def test_event_dataclass_creation() -> None:
    """Ensure the Event dataclass stores the expected fields."""
    snapshot = np.zeros((4, 4, 3), dtype=np.uint8)
    event = Event(
        type="fire_smoke",
        confidence=0.92,
        timestamp="2026-04-01T00:00:00Z",
        frame_snapshot=snapshot,
        camera_id="CAM_001",
    )

    assert event.type == "fire_smoke"
    assert event.confidence == 0.92
    assert event.timestamp == "2026-04-01T00:00:00Z"
    assert event.camera_id == "CAM_001"
    assert np.array_equal(event.frame_snapshot, snapshot)


def test_consecutive_frame_confirmation_logic() -> None:
    """Emit an event only after 4 positive detections in a 6-frame window."""
    model = DummyModel(
        predictions=[
            [{"event_type": "fire_smoke", "confidence": 0.91}],
            [{"event_type": "fire_smoke", "confidence": 0.91}],
            [{"event_type": "fire_smoke", "confidence": 0.91}],
            [{"event_type": "fire_smoke", "confidence": 0.91}],
        ]
    )
    detector = Detector(
        confidence_threshold=0.75,
        frame_confirmation_n=4,
        frame_confirmation_m=6,
        model=model,
    )
    frame = np.zeros((8, 8, 3), dtype=np.uint8)
    timestamp = datetime(2026, 4, 1, tzinfo=timezone.utc)

    assert detector.detect(frame, "CAM_001", timestamp=timestamp) is None
    assert detector.detect(frame, "CAM_001", timestamp=timestamp) is None
    assert detector.detect(frame, "CAM_001", timestamp=timestamp) is None

    event = detector.detect(frame, "CAM_001", timestamp=timestamp)
    assert event is not None
    assert event.type == "fire_smoke"
    assert event.confidence == 0.91


def test_confidence_threshold_filtering() -> None:
    """Ignore detections below the configured confidence threshold."""
    model = DummyModel(
        predictions=[
            [{"event_type": "intrusion", "confidence": 0.50}],
            [{"event_type": "intrusion", "confidence": 0.50}],
            [{"event_type": "intrusion", "confidence": 0.50}],
            [{"event_type": "intrusion", "confidence": 0.50}],
        ]
    )
    detector = Detector(
        confidence_threshold=0.75,
        frame_confirmation_n=4,
        frame_confirmation_m=6,
        model=model,
    )
    frame = np.zeros((8, 8, 3), dtype=np.uint8)
    timestamp = datetime(2026, 4, 1, tzinfo=timezone.utc)

    assert detector.detect(frame, "CAM_001", timestamp=timestamp) is None
    assert detector.detect(frame, "CAM_001", timestamp=timestamp) is None
    assert detector.detect(frame, "CAM_001", timestamp=timestamp) is None
    assert detector.detect(frame, "CAM_001", timestamp=timestamp) is None
