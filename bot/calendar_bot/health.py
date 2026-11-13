"""Healthchecks.io ping (ADR 0010, NFR-007)."""
from __future__ import annotations

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

PING_INTERVAL_SECONDS = 300


async def ping_forever(url: str, interval: float = PING_INTERVAL_SECONDS) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            try:
                await client.get(url)
            except httpx.HTTPError as error:
                logger.warning("Health ping failed: %s", type(error).__name__)
            await asyncio.sleep(interval)
