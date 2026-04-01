"""Video clip writing utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2


def _coerce_timestamp(value: datetime | str) -> datetime:
    """Convert a timestamp value into an aware UTC datetime."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _safe_filename(timestamp: datetime) -> str:
    """Return a filesystem-safe ISO-like timestamp for filenames."""
    return timestamp.isoformat().replace(":", "-")


class ClipWriter:
    """Write buffered frames to an MP4 clip on disk."""

    def __init__(self, events_dir: str | Path = "./events", fps: float = 10.0) -> None:
        """Initialize the clip writer."""
        self.events_dir = Path(events_dir)
        self.fps = max(float(fps), 1.0)

    def write_clip(
        self,
        frames: list[tuple[Any, datetime]],
        event_type: str,
        event_timestamp: datetime | str,
    ) -> str:
        """Write a list of frames to an MP4 clip and return the absolute path."""
        if not frames:
            raise ValueError("Cannot write a clip without frames.")

        timestamp = _coerce_timestamp(event_timestamp)
        output_dir = self.events_dir / timestamp.strftime("%Y-%m-%d") / event_type
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{_safe_filename(timestamp)}.mp4"

        first_frame = frames[0][0]
        height, width = first_frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_path), fourcc, self.fps, (width, height))

        if not writer.isOpened():
            raise RuntimeError(f"Failed to open video writer for {output_path}.")

        try:
            for frame, _ in frames:
                writer.write(frame)
        finally:
            writer.release()

        return str(output_path.resolve())
