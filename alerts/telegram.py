"""Telegram alert delivery for confirmed events."""

from __future__ import annotations

from io import BytesIO
import logging
import os
from typing import Any

import cv2
from dotenv import load_dotenv


class TelegramAlerter:
    """Send event notifications to Telegram."""

    def __init__(self) -> None:
        """Load Telegram bot configuration from the environment."""
        load_dotenv()
        self.logger = logging.getLogger("alerts.telegram")
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    async def send_event_alert(
        self,
        event: Any,
        tx_hash: str,
        ipfs_url: str,
        clip_path: str,
    ) -> None:
        """Send an event alert and optional snapshot to Telegram."""
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Skipping Telegram alert because TELEGRAM_BOT_TOKEN is not configured.")
            return

        from telegram import Bot

        bot = Bot(token=self.bot_token)
        explorer_url = tx_hash if tx_hash.startswith("http") else tx_hash
        message = (
            f"🚨 {str(event.type).upper()} DETECTED\n"
            f"📍 Camera: {event.camera_id}\n"
            f"🕐 Time: {event.timestamp}\n"
            f"🎯 Confidence: {int(round(float(event.confidence) * 100))}%\n"
            f"🔗 Avalanche TX: {explorer_url}\n"
            f"📹 Evidence: {ipfs_url}"
        )
        await bot.send_message(chat_id=self.chat_id, text=message)

        success, encoded = cv2.imencode(".jpg", event.frame_snapshot)
        if success:
            await self.send_snapshot(self.chat_id, encoded.tobytes())

        self.logger.info("Telegram alert sent for clip %s", clip_path)

    async def send_snapshot(self, chat_id: str, image_bytes: bytes) -> None:
        """Send a frame snapshot to Telegram."""
        if not self.bot_token:
            self.logger.warning("Skipping Telegram snapshot because TELEGRAM_BOT_TOKEN is not configured.")
            return

        from telegram import Bot

        bot = Bot(token=self.bot_token)
        await bot.send_photo(chat_id=chat_id, photo=BytesIO(image_bytes))
