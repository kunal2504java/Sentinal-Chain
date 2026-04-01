"""YOLOv8-backed event detection logic."""

from __future__ import annotations

from collections import deque
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
    bbox: tuple[float, float, float, float] | None = None


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
        nms_iou_threshold: float = 0.45,
        min_bbox_area: float = 400.0,
        ignore_zones: list[list[list[float]]] | None = None,
        model: Any | None = None,
    ) -> None:
        """Initialize the detector."""
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.frame_confirmation_n = frame_confirmation_n
        self.frame_confirmation_m = frame_confirmation_m
        self.nms_iou_threshold = nms_iou_threshold
        self.min_bbox_area = min_bbox_area
        self.ignore_zones = ignore_zones or []
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
        filtered = [
            detection
            for detection in normalized
            if detection.confidence >= self.confidence_threshold
            and self._passes_bbox_filters(detection)
        ]
        return self._apply_nms(filtered)

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
                bbox_value = item.get("bbox")
                bbox = tuple(float(v) for v in bbox_value) if bbox_value else None
                return [Detection(event_type=event_type, confidence=float(confidence), bbox=bbox)]
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
                    bbox=tuple(float(v) for v in box.xyxy[0].tolist()),
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

    def _passes_bbox_filters(self, detection: Detection) -> bool:
        """Return whether a detection passes area and ignore-zone filters."""
        if detection.bbox is None:
            return True
        x1, y1, x2, y2 = detection.bbox
        area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        if area < self.min_bbox_area:
            return False
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        for polygon in self.ignore_zones:
            if self._point_in_polygon(center_x, center_y, polygon):
                return False
        return True

    def _apply_nms(self, detections: list[Detection]) -> list[Detection]:
        """Apply class-wise non-max suppression."""
        grouped: dict[str, list[Detection]] = {}
        for detection in detections:
            grouped.setdefault(detection.event_type, []).append(detection)

        kept: list[Detection] = []
        for group in grouped.values():
            ordered = sorted(group, key=lambda item: item.confidence, reverse=True)
            selected: list[Detection] = []
            while ordered:
                candidate = ordered.pop(0)
                selected.append(candidate)
                ordered = [
                    item
                    for item in ordered
                    if self._iou(candidate.bbox, item.bbox) < self.nms_iou_threshold
                ]
            kept.extend(selected)
        return kept

    def _iou(
        self,
        first: tuple[float, float, float, float] | None,
        second: tuple[float, float, float, float] | None,
    ) -> float:
        """Compute intersection-over-union for two boxes."""
        if first is None or second is None:
            return 0.0
        ax1, ay1, ax2, ay2 = first
        bx1, by1, bx2, by2 = second
        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)
        inter_area = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)
        area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
        area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
        union = area_a + area_b - inter_area
        if union <= 0:
            return 0.0
        return inter_area / union

    def _point_in_polygon(self, x: float, y: float, polygon: list[list[float]]) -> bool:
        """Return whether a point lies inside a polygon."""
        inside = False
        if len(polygon) < 3:
            return False
        prev_x, prev_y = polygon[-1]
        for current_x, current_y in polygon:
            crosses = ((current_y > y) != (prev_y > y)) and (
                x < (prev_x - current_x) * (y - current_y) / ((prev_y - current_y) or 1e-9) + current_x
            )
            if crosses:
                inside = not inside
            prev_x, prev_y = current_x, current_y
        return inside
