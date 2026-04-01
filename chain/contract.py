"""Avalanche blockchain integration for SentinelChain events."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from chain.queue import PendingEventQueue


class AvalancheLogger:
    """Submit and verify event evidence records on Avalanche."""

    def __init__(
        self,
        abi_path: str | Path = Path("chain") / "abi.json",
        sqlite_path: str | None = None,
    ) -> None:
        """Connect to Avalanche RPC and prepare the contract client."""
        load_dotenv()

        from web3 import Web3

        self.rpc_url = os.getenv("RPC_URL", "https://api.avax-test.network/ext/bc/C/rpc")
        self.chain_id = int(os.getenv("CHAIN_ID", "43113"))
        self.private_key = os.getenv("PRIVATE_KEY")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.camera_location = os.getenv("CAMERA_LOCATION", "Unknown")
        self.abi_path = Path(abi_path)
        self.sqlite_path = sqlite_path or os.getenv("SQLITE_PATH", "./sentinelchain.db")

        if not self.private_key:
            raise ValueError("PRIVATE_KEY is required.")
        if not self.contract_address:
            raise ValueError("CONTRACT_ADDRESS is required.")

        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.web3.is_connected():
            raise ConnectionError(f"Unable to connect to RPC at {self.rpc_url}")

        with self.abi_path.open("r", encoding="utf-8") as file_handle:
            self.abi = json.load(file_handle)

        self.account = self.web3.eth.account.from_key(self.private_key)
        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(self.contract_address),
            abi=self.abi,
        )
        self.queue = PendingEventQueue(sqlite_path=self.sqlite_path)

    def log_event(self, event: Any, clip_hash: str, ipfs_cid: str) -> str:
        """Submit an event to Avalanche or queue it for retry on failure."""
        try:
            return self.submit_queued_event(
                event_payload=self._event_payload(event),
                clip_hash=clip_hash,
                ipfs_cid=ipfs_cid,
            )
        except Exception:
            local_id = self.queue.add_to_queue(event, clip_hash, ipfs_cid)
            return f"queued:{local_id}"

    def submit_queued_event(
        self,
        event_payload: dict[str, Any],
        clip_hash: str,
        ipfs_cid: str,
    ) -> str:
        """Submit a previously serialized event payload to Avalanche."""
        confidence = int(round(float(event_payload["confidence"]) * 100))
        nonce = self.web3.eth.get_transaction_count(self.account.address)
        transaction = self.contract.functions.logEvent(
            str(event_payload["type"]),
            str(event_payload["camera_id"]),
            self.camera_location,
            clip_hash,
            ipfs_cid,
            confidence,
        ).build_transaction(
            {
                "chainId": self.chain_id,
                "from": self.account.address,
                "nonce": nonce,
                "gas": 500000,
                "gasPrice": self.web3.eth.gas_price,
            }
        )
        signed = self.account.sign_transaction(transaction)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt["transactionHash"].hex()

    def verify_event(self, event_id: int) -> dict[str, Any]:
        """Fetch and normalize an on-chain event record."""
        result = self.contract.functions.getEvent(event_id).call()
        return {
            "eventType": result[0],
            "timestamp": result[1],
            "cameraId": result[2],
            "location": result[3],
            "clipHash": result[4],
            "ipfsCid": result[5],
            "confidence": result[6],
            "reportedBy": result[7],
        }

    def get_explorer_url(self, tx_hash: str) -> str:
        """Return the Snowtrace URL for a transaction hash."""
        base_url = "https://testnet.snowtrace.io/tx"
        if self.chain_id == 43114:
            base_url = "https://snowtrace.io/tx"
        return f"{base_url}/{tx_hash}"

    def _event_payload(self, event: Any) -> dict[str, Any]:
        """Normalize an event-like object into a serializable payload."""
        if is_dataclass(event):
            payload = asdict(event)
        elif isinstance(event, dict):
            payload = dict(event)
        else:
            payload = {
                "type": getattr(event, "type"),
                "confidence": getattr(event, "confidence"),
                "timestamp": getattr(event, "timestamp"),
                "camera_id": getattr(event, "camera_id"),
            }

        payload.pop("frame_snapshot", None)
        return payload
