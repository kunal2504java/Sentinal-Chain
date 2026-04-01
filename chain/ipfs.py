"""Pinata IPFS client for clip uploads."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import requests


class PinataClient:
    """Upload and verify evidence clips via Pinata."""

    def __init__(self) -> None:
        """Load Pinata credentials from the environment."""
        load_dotenv()
        self.api_key = os.getenv("PINATA_API_KEY", "")
        self.secret = os.getenv("PINATA_SECRET", "")
        self.base_url = "https://api.pinata.cloud"
        self.gateway_base = "https://gateway.pinata.cloud/ipfs"

    def upload_clip(self, filepath: str, metadata: dict[str, Any]) -> str:
        """Upload a clip to Pinata and return the resulting CID."""
        if not self.api_key or not self.secret:
            raise ValueError("PINATA_API_KEY and PINATA_SECRET must be configured.")

        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Clip file not found: {filepath}")

        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret,
        }
        payload = {
            "pinataMetadata": json.dumps({"name": path.name, "keyvalues": metadata}),
        }

        with path.open("rb") as clip_file:
            response = requests.post(
                f"{self.base_url}/pinning/pinFileToIPFS",
                headers=headers,
                data=payload,
                files={"file": (path.name, clip_file, "video/mp4")},
                timeout=120,
            )

        response.raise_for_status()
        body = response.json()
        cid = body.get("IpfsHash")
        if not cid:
            raise RuntimeError("Pinata response did not include an IpfsHash.")
        return str(cid)

    def get_ipfs_url(self, cid: str) -> str:
        """Return the public Pinata gateway URL for a CID."""
        return f"{self.gateway_base}/{cid}"

    def verify_upload(self, cid: str) -> bool:
        """Check whether the uploaded CID is reachable on the gateway."""
        response = requests.get(self.get_ipfs_url(cid), timeout=30)
        return response.ok
