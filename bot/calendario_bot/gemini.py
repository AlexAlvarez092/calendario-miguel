"""Gemini client that reads the schedule photo (ADR 0001, NFR-002)."""
from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import httpx

from .schedule import DayReading, ReadResult, parse_time

logger = logging.getLogger(__name__)

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TEMPORARY_STATUS = {429, 500, 502, 503, 504}
RETRY_WAITS = (10, 30, 60)
ATTEMPT_TIMEOUT_SECONDS = 45

PROMPT = """You are reading a photo of a printed monthly work schedule.
The table has one block per week, and each block has one row per person with one column per day.

Rules:
- Use ONLY the rows labeled "MIGUEL" (one per week block). Ignore every other person.
- Ignore the yellow highlighting of cells and the last column of each block.
- The photo can cover any period (a few weeks, or part of a month, possibly crossing into the next month). Return the days in the order they appear, week block after week block.
- Read the month and year of the FIRST day you return from the table header (for example "nov-26" is November 2026). If you cannot read them, use null.
- Return one item per day column of Miguel's rows, using the day-of-month number printed in the column header.
- Never guess. If a cell is hard to read or you are not sure, set "uncertain" to true.

For each day return:
- "day": the day of the month (integer).
- "raw_text": the literal text of the cell exactly as printed.
- "kind": "shift" if the cell is a start-end time such as 10-18 or 18-02; "non_working" if the cell marks a day without work (for example DESCANSO or VACACIONES); "unknown" for anything else. A cell with other words, such as "debido 02-11", is "unknown".
- "start" and "end": the shift times as "HH:MM" in 24 hours (16-00 ends at "00:00"), or null when it is not a shift.
- "non_working_type": the printed marker of a non-working day, or null.
- "ignored_annotations": annotations printed in the cell that do not change whether Miguel works or the times of the shift (for example PEDIDO, HT, INV HORA).
- "uncertain": true if you are not sure about this cell.

Answer only with JSON: {"month": 1-12 or null, "year": 4 digits or null, "days": [...]}"""


class ReadingError(Exception):
    """The photo could not be read. The message is safe to show to Miguel."""


class GeminiReader:
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.5-flash-lite",
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        client_factory: Optional[Callable[[], httpx.AsyncClient]] = None,
    ):
        self.api_key = api_key
        self.model = model
        self._sleep = sleep
        self._client_factory = client_factory or (
            lambda: httpx.AsyncClient(timeout=ATTEMPT_TIMEOUT_SECONDS)
        )

    async def read(self, image: bytes, mime_type: str = "image/jpeg") -> ReadResult:
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": PROMPT},
                        {"inline_data": {"mime_type": mime_type, "data": base64.b64encode(image).decode()}},
                    ]
                }
            ],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
        }
        payload = await self._post_with_retries(body)
        return parse_response(payload)

    async def _post_with_retries(self, body: Dict[str, Any]) -> Dict[str, Any]:
        waits = (0,) + RETRY_WAITS
        for attempt, wait in enumerate(waits, start=1):
            if wait:
                await self._sleep(wait)
            try:
                async with self._client_factory() as client:
                    response = await client.post(
                        API_URL.format(model=self.model),
                        json=body,
                        headers={"x-goog-api-key": self.api_key},
                    )
            except (httpx.TimeoutException, httpx.TransportError) as error:
                logger.warning("Gemini attempt %d failed: %s", attempt, type(error).__name__)
                continue
            if response.status_code in TEMPORARY_STATUS:
                logger.warning("Gemini attempt %d returned HTTP %d", attempt, response.status_code)
                continue
            if response.status_code != 200:
                logger.error("Gemini returned HTTP %d", response.status_code)
                raise ReadingError("El servicio de IA ha rechazado la petición.")
            return response.json()
        raise ReadingError("El servicio de IA no responde ahora mismo.")


def parse_response(payload: Dict[str, Any]) -> ReadResult:
    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(text)
        days: List[DayReading] = []
        for item in data["days"]:
            days.append(_parse_day(item))
        return ReadResult(
            month=_optional_int(data.get("month")),
            year=_optional_int(data.get("year")),
            days=days,
        )
    except (KeyError, IndexError, TypeError, ValueError) as error:
        logger.error("Invalid Gemini response: %r", error)
        raise ReadingError("No he entendido la respuesta del servicio de IA.") from error


def _optional_int(value: Any) -> Optional[int]:
    return int(value) if value is not None else None


def _parse_time(value: Any):
    return parse_time(value) if isinstance(value, str) else None


def _parse_day(item: Dict[str, Any]) -> DayReading:
    kind = item.get("kind")
    start, end = _parse_time(item.get("start")), _parse_time(item.get("end"))
    if kind == "shift" and (start is None or end is None):
        kind = "unknown"
    if kind not in ("shift", "non_working"):
        kind = "unknown"
    return DayReading(
        day=int(item["day"]),
        raw_text=str(item.get("raw_text") or ""),
        kind=kind,
        start=start,
        end=end,
        off_type=item.get("non_working_type") or None,
        ignored=[str(a) for a in (item.get("ignored_annotations") or [])],
        uncertain=bool(item.get("uncertain")),
    )
