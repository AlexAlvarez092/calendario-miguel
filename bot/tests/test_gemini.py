import json

import httpx
import pytest

from calendario_bot.gemini import GeminiReader, ReadingError, parse_response


def ok_payload(days):
    text = json.dumps({"month": 11, "year": 2026, "days": days})
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


class Client:
    def __init__(self, handler):
        self.handler = handler

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, *args, **kwargs):
        return self.handler()


def reader(handler, waits):
    async def sleep(seconds):
        waits.append(seconds)

    return GeminiReader("key", sleep=sleep, client_factory=lambda: Client(handler))


async def test_retries_temporary_errors_with_waits():
    waits, calls = [], []

    def handler():
        calls.append(1)
        if len(calls) < 3:
            return httpx.Response(503)
        return httpx.Response(200, json=ok_payload([{"day": 1, "raw_text": "10-18", "kind": "shift", "start": "10:00", "end": "18:00"}]))

    result = await reader(handler, waits).read(b"img")
    assert waits == [10, 30]
    assert result.month == 11 and result.days[0].start.hour == 10


async def test_gives_up_after_retries():
    waits = []
    with pytest.raises(ReadingError):
        await reader(lambda: httpx.Response(429), waits).read(b"img")
    assert waits == [10, 30, 60]


async def test_non_temporary_error_not_retried():
    waits = []
    with pytest.raises(ReadingError):
        await reader(lambda: httpx.Response(400), waits).read(b"img")
    assert waits == []


def test_invalid_json_is_reading_error():
    with pytest.raises(ReadingError):
        parse_response({"candidates": [{"content": {"parts": [{"text": "not json"}]}}]})


def test_shift_without_times_becomes_unknown():
    result = parse_response(ok_payload([{"day": 1, "raw_text": "10-18", "kind": "shift"}]))
    assert result.days[0].kind == "unknown"
