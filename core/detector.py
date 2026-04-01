"""YOLOv8-backed event detection logic."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import numpy as np


SUPPORTED_EVENT_TYPES = ("fire_smoke", "person_down", "intrusion")


@dataclass(slots=True)
class Event:
    """A confirmed surveillance event."""

    type: str
    confidence: float
    timestamp: str
    frame_snapshot: np.ndarray
    camera_id: str


@dataclass(slots=True)
class Detection:
    """A single candidate detection extracted from model output."""

    event_type: str
    confidence: float


def _utc_timestamp(now: datetime | None = None) -> datetime:
    """Return an aware UTC datetime."""
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


class Detector:
    """Wrap YOLO inference and consecutive-frame confirmation logic."""

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.75,
        frame_confirmation_n: int = 4,
        frame_confirmation_m: int = 6,
        model: Any | None = None,
    ) -> None:
        """Initialize the detector."""
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.frame_confirmation_n = frame_confirmation_n
        self.frame_confirmation_m = frame_confirmation_m
        self.model = model or self._load_model(model_path)
        self._history: dict[str, deque[bool]] = {
            event_type: deque(maxlen=frame_confirmation_m)
            for event_type in SUPPORTED_EVENT_TYPES
        }
        self._active_events: set[str] = set()

    def _load_model(self, model_path: str) -> Any:
        """Load a YOLO model lazily so tests can run without the dependency."""
        from ultralytics import YOLO

        return YOLO(model_path)

    def detect(
        self,
        frame: np.ndarray,
        camera_id: str,
        timestamp: datetime | None = None,
    ) -> Event | None:
        """Run inference on a frame and return a confirmed event when detected."""
        current_time = _utc_timestamp(timestamp)
        detections = self._predict(frame)
        best_by_type = self._best_detections_by_type(detections)

        for event_type in SUPPORTED_EVENT_TYPES:
            is_present = event_type in best_by_type
            history = self._history[event_type]
            history.append(is_present)

            if is_present and sum(history) >= self.frame_confirmation_n:
                if event_type not in self._active_events:
                    self._active_events.add(event_type)
                    return Event(
                        type=event_type,
                        confidence=best_by_type[event_type].confidence,
                        timestamp=current_time.isoformat().replace("+00:00", "Z"),
                        frame_snapshot=np.copy(frame),
                        camera_id=camera_id,
                    )
            elif not is_present and sum(history) < self.frame_confirmation_n:
                self._active_events.discard(event_type)

        return None

    def _predict(self, frame: np.ndarray) -> list[Detection]:
        """Convert raw model output into normalized detections."""
        raw_results = self.model.predict(frame, verbose=False)
        normalized = self._normalize_results(raw_results)
        return [
            detection
            for detection in normalized
            if detection.confidence >= self.confidence_threshold
        ]

    def _normalize_results(self, raw_results: Any) -> list[Detection]:
        """Normalize a variety of model result shapes into Detection instances."""
        detections: list[Detection] = []
        for item in raw_results or []:
            detections.extend(self._normalize_result_item(item))
        return detections

    def _normalize_result_item(self, item: Any) -> list[Detection]:
        """Normalize a single result item."""
        if isinstance(item, Detection):
            return [item]

        if isinstance(item, dict):
            event_type = item.get("event_type")
            confidence = item.get("confidence", 0.0)
            if event_type in SUPPORTED_EVENT_TYPES:
                return [Detection(event_type=event_type, confidence=float(confidence))]
            return []

        if hasattr(item, "boxes"):
            return self._normalize_yolo_result(item)

        return []

    def _normalize_yolo_result(self, result: Any) -> list[Detection]:
        """Normalize an Ultralytics result object into Detection instances."""
        detections: list[Detection] = []
        names = getattr(result, "names", {}) or getattr(self.model, "names", {})
        for box in result.boxes:
            class_index = int(box.cls[0])
            label = str(names.get(class_index, class_index)).lower()
            event_type = self._map_label_to_event_type(label)
            if event_type is None:
                continue
            detections.append(
                Detection(
                    event_type=event_type,
                    confidence=float(box.conf[0]),
                )
            )
        return detections

    def _map_label_to_event_type(self, label: str) -> str | None:
        """Map model class labels to supported event types."""
        if label in {"fire", "smoke", "fire_smoke"}:
            return "fire_smoke"
        if label in {"person_down", "fallen_person", "fall", "accident"}:
            return "person_down"
        if label in {"intrusion", "trespass", "unauthorized_person"}:
            return "intrusion"
        return None

    def _best_detections_by_type(self, detections: list[Detection]) -> dict[str, Detection]:
        """Keep the highest-confidence detection for each event type."""
        best: dict[str, Detection] = {}
        for detection in detections:
            existing = best.get(detection.event_type)
            if existing is None or detection.confidence > existing.confidence:
                best[detection.event_type] = detection
        return best
