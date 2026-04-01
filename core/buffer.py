"""Rolling video frame buffer."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Any


def _coerce_timestamp(value: datetime | str) -> datetime:
    """Convert a timestamp value into an aware UTC datetime."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class RollingBuffer:
    """Store a bounded rolling window of frames and timestamps."""

    def __init__(self, fps: float, buffer_seconds: int = 60) -> None:
        """Initialize the rolling buffer."""
        self.fps = max(float(fps), 1.0)
        self.buffer_seconds = buffer_seconds
        self._frames: deque[tuple[Any, datetime]] = deque(
            maxlen=max(1, ceil(self.fps * buffer_seconds))
        )

    def push_frame(self, frame: Any, timestamp: datetime | str) -> None:
        """Append a frame and its timestamp to the rolling buffer."""
        self._frames.append((frame, _coerce_timestamp(timestamp)))

    def get_clip(
        self,
        seconds_before: int,
        seconds_after: int,
        event_timestamp: datetime | str,
    ) -> list[tuple[Any, datetime]]:
        """Return frames around an event timestamp."""
        center = _coerce_timestamp(event_timestamp)
        window_start = center - timedelta(seconds=seconds_before)
        window_end = center + timedelta(seconds=seconds_after)
        return [
            (frame, timestamp)
            for frame, timestamp in self._frames
            if window_start <= timestamp <= window_end
        ]
