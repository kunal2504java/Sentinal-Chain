"""Application configuration loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _get_env(name: str, default: str) -> str:
    """Return an environment variable value or a default."""
    return os.getenv(name, default)


def _get_int(name: str, default: int) -> int:
    """Return an integer environment variable value or a default."""
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    return int(raw_value)


def _get_float(name: str, default: float) -> float:
    """Return a float environment variable value or a default."""
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    return float(raw_value)


def _parse_camera_source(raw_value: str | None) -> int | str:
    """Parse a camera source string into an integer index or URL."""
    if raw_value is None or raw_value == "":
        return 0
    if raw_value.isdigit():
        return int(raw_value)
    return raw_value


@dataclass(slots=True)
class Settings:
    """Runtime configuration for the detection pipeline."""

    camera_source: int | str
    camera_id: str
    camera_location: str
    model_path: str
    confidence_threshold: float
    frame_confirmation_n: int
    frame_confirmation_m: int
    buffer_seconds: int
    clip_before_seconds: int
    clip_after_seconds: int
    events_dir: Path
    log_level: str


def load_settings() -> Settings:
    """Load application settings from environment variables."""
    return Settings(
        camera_source=_parse_camera_source(os.getenv("CAMERA_SOURCE")),
        camera_id=_get_env("CAMERA_ID", "CAM_001"),
        camera_location=_get_env("CAMERA_LOCATION", "Building A, Gate 2"),
        model_path=_get_env("MODEL_PATH", "yolov8n.pt"),
        confidence_threshold=_get_float("CONFIDENCE_THRESHOLD", 0.75),
        frame_confirmation_n=_get_int("FRAME_CONFIRMATION_N", 4),
        frame_confirmation_m=_get_int("FRAME_CONFIRMATION_M", 6),
        buffer_seconds=_get_int("BUFFER_SECONDS", 60),
        clip_before_seconds=_get_int("CLIP_BEFORE_SECONDS", 15),
        clip_after_seconds=_get_int("CLIP_AFTER_SECONDS", 15),
        events_dir=Path(_get_env("EVENTS_DIR", "./events")),
        log_level=_get_env("LOG_LEVEL", "INFO"),
    )
