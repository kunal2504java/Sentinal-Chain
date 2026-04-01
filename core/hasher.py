"""File hashing utilities."""

from __future__ import annotations

import hashlib


def hash_file(filepath: str) -> str:
    """Return the SHA-256 hash for a file as a lowercase hex string."""
    digest = hashlib.sha256()
    with open(filepath, "rb") as file_handle:
        while chunk := file_handle.read(8192):
            digest.update(chunk)
    return digest.hexdigest()
