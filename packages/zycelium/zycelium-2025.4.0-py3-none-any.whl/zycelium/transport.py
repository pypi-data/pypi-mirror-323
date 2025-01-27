"""Zycelium Agent Transport"""

import asyncio
import json
from typing import Callable, Optional

import nats
from nats.aio.client import Client

from zycelium.logging import get_logger

CONNECT_TIMEOUT = 10  # seconds
OPERATION_TIMEOUT = 5  # seconds
DRAIN_TIMEOUT = 2  # seconds


class NatsTransport:
    def __init__(self, log_level: str) -> None:
        self._client: Optional[Client] = None
        self._connected = False
        self._subscriptions = {}  # track subscriptions by subject
        self._is_draining = False
        self.logger = get_logger(__name__, log_level)
        self._request_semaphore = asyncio.Semaphore(10)  # Allow 10 concurrent requests

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def is_draining(self) -> bool:
        return self._is_draining

    async def _error_cb(self, e):
        """Error callback for NATS."""
        self.logger.error(f"NATS error: {e}")

    async def _reconnected_cb(self):
        """Reconnection callback for NATS."""
        self.logger.info("Reconnected to NATS")
        self._connected = True

    async def _disconnected_cb(self):
        """Disconnection callback for NATS."""
        self.logger.info("Disconnected from NATS")
        self._connected = False

    async def connect(self, nats_uri: str, nats_token: Optional[str] = None) -> None:
        options = {
            "servers": [nats_uri],
            "error_cb": self._error_cb,
            "reconnected_cb": self._reconnected_cb,
            "disconnected_cb": self._disconnected_cb,
        }
        if nats_token:
            options["token"] = nats_token

        try:
            async with asyncio.timeout(CONNECT_TIMEOUT):
                self._client = await nats.connect(**options)
                self._connected = True
                self.logger.info("Connected to NATS")
        except Exception as e:
            self.logger.error(f"Failed to connect to NATS: {e}")

    async def disconnect(self) -> None:
        if self._client:
            try:
                # Unsubscribe from all subjects first
                for subject in list(self._subscriptions.keys()):
                    await self.unsubscribe(subject)
                await self._client.close()
            except Exception as e:
                self.logger.warning(f"Error during disconnect: {e}")
            finally:
                self._connected = False
                self._subscriptions.clear()

    async def publish(self, subject: str, data: bytes) -> None:
        if not self._client:
            self.logger.error(f"Failed to publish to {subject}: not connected")
            return
        try:
            async with asyncio.timeout(OPERATION_TIMEOUT):
                await self._client.publish(subject, data)
        except Exception as e:
            self.logger.error(f"Error publishing to {subject}: {e}")

    async def subscribe(self, subject: str, callback: Callable) -> None:
        if not self._client:
            self.logger.error(f"Failed to subscribe to {subject}: not connected")
            return
        try:
            self.logger.debug(f"Attempting to subscribe to: {subject}")
            sub = await self._client.subscribe(subject, cb=callback)
            self._subscriptions[subject] = sub
            self.logger.debug(f"Successfully subscribed to: {subject}")
            self.logger.debug(
                f"Current subscriptions: {list(self._subscriptions.keys())}"
            )
        except Exception as e:
            self.logger.error(f"Error subscribing to {subject}: {e}")

    async def unsubscribe(self, subject: str) -> None:
        """Unsubscribe from a subject."""
        if not self._client or not self._client.is_connected:
            # Connection already closed, just remove from local tracking
            self._subscriptions.pop(subject, None)
            self.logger.debug(f"Removed subscription tracking for: {subject}")
            return

        try:
            if sub := self._subscriptions.pop(subject, None):
                # Check if subscription is still active before unsubscribing
                if not sub._closed:
                    await sub.unsubscribe()
                    self.logger.debug(f"Unsubscribed from: {subject}")
            else:
                pass
        except Exception as e:
            self.logger.error(f"Error unsubscribing from {subject}: {e}")
            # Still remove from tracking even if unsubscribe fails
            self._subscriptions.pop(subject, None)

    async def request(self, subject: str, data: bytes) -> Optional[bytes]:
        if not self._client:
            self.logger.error(f"Failed to send request to {subject}: not connected")
            return None

        async with self._request_semaphore:  # Control concurrent requests
            try:
                self.logger.debug(f"Sending request to {subject} with data: {data!r}")
                response = await self._client.request(subject, data)
                self.logger.debug(
                    f"Received response from {subject}: {response.data!r}"
                )
                return response
            except asyncio.TimeoutError:
                self.logger.error(
                    f"Request to {subject} timed out after {OPERATION_TIMEOUT}s"
                )
                return None
            except Exception as e:
                self.logger.error(f"Error requesting from {subject}: {e}")
                return None

    async def drain(self) -> None:
        if not self._client:
            self.logger.warning("Failed to drain: not connected")
            return
        try:
            self._is_draining = True
            self.logger.info(
                f"Starting NATS drain operation (timeout: {DRAIN_TIMEOUT}s)"
            )
            self.logger.info("Please wait, completing in-flight messages...")
            await asyncio.wait_for(self._client.drain(), timeout=DRAIN_TIMEOUT)
        except asyncio.TimeoutError:
            self.logger.warning(f"Drain operation timed out after {DRAIN_TIMEOUT}s")
        except Exception as e:
            self.logger.warning(f"Error during drain: {e}")
        finally:
            self._is_draining = False
            self.logger.info("Drain operation completed")
