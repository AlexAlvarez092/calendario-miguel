"""Readings of the schedule photo, their validation (FR-004) and input parsing."""
from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, time
from typing import Dict, List, Optional, Tuple

from .events import Entry

NON_WORKING_TYPES = ("Descanso", "Vacaciones", "Festivo", "Compensatorio")

_RANGE_RE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*[-–—]\s*(\d{1,2})(?::(\d{2}))?")
_TIME_RE = re.compile(r"^(\d{1,2})(?::(\d{2}))?$")


@dataclass
class DayReading:
    day: int
    raw_text: str
    kind: str  # "shift", "non_working" or "unknown"
    start: Optional[time] = None
    end: Optional[time] = None
    off_type: Optional[str] = None
    ignored: List[str] = field(default_factory=list)
    uncertain: bool = False


@dataclass
class ReadResult:
    month: Optional[int]
    year: Optional[int]
    days: List[DayReading]


def _make_time(hour: str, minute: Optional[str]) -> Optional[time]:
    h, m = int(hour), int(minute or 0)
    if 0 <= h <= 23 and 0 <= m <= 59:
        return time(h, m)
    return None


def parse_time(text: str) -> Optional[time]:
    match = _TIME_RE.match(text.strip())
    return _make_time(match.group(1), match.group(2)) if match else None


def parse_shift_range(text: str) -> Optional[Tuple[time, time]]:
    """Parse `10-18` or `18:00-02:00` (the whole text must be the range)."""
    match = _RANGE_RE.fullmatch(text.strip())
    if not match:
        return None
    start = _make_time(match.group(1), match.group(2))
    end = _make_time(match.group(3), match.group(4))
    if start is None or end is None or start == end:
        return None
    return start, end


def parse_date(text: str) -> Optional[date]:
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text.strip())
    if not match:
        return None
    try:
        return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
    except ValueError:
        return None


def parse_month(text: str) -> Optional[Tuple[int, int]]:
    """Parse `mm/yyyy` into (year, month)."""
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", text.strip())
    if not match or not 1 <= int(match.group(1)) <= 12:
        return None
    return int(match.group(2)), int(match.group(1))


def normalize_label(text: str) -> str:
    return text.strip().capitalize()


def parse_day_answer(text: str, day: date) -> Optional[Entry]:
    """Parse Miguel's answer to a clarification: a time range or a known non-working type."""
    shift = parse_shift_range(text)
    if shift:
        return Entry.shift(day, shift[0], shift[1])
    for known in NON_WORKING_TYPES:
        if text.strip().casefold() == known.casefold():
            return Entry.off(day, known)
    return None


def _leftover(raw: str, explained: List[str]) -> str:
    """Text of the cell that nothing explains."""
    rest = raw.casefold()
    for part in explained:
        if part.strip():
            rest = rest.replace(part.strip().casefold(), " ")
    return re.sub(r"[\W_]+", "", rest)


def is_understood(reading: DayReading) -> bool:
    """FR-004: do not trust the AI service; check its interpretation against the literal text."""
    if reading.uncertain or reading.kind not in ("shift", "non_working"):
        return False
    if reading.kind == "shift":
        match = _RANGE_RE.search(reading.raw_text)
        if not match or reading.start is None or reading.end is None:
            return False
        literal = (
            _make_time(match.group(1), match.group(2)),
            _make_time(match.group(3), match.group(4)),
        )
        if literal != (reading.start, reading.end):
            return False
        rest = reading.raw_text.replace(match.group(0), " ", 1)
        return _leftover(rest, reading.ignored) == ""
    if not reading.off_type:
        return False
    return _leftover(reading.raw_text, [reading.off_type] + reading.ignored) == ""


@dataclass
class Analysis:
    understood: Dict[int, DayReading]
    unclear: List[int]
    missing: List[int]
    outside: List[int]


def analyze(days: List[DayReading], year: int, month: int) -> Analysis:
    """Classify the days read from the photo for the given month."""
    last_day = calendar.monthrange(year, month)[1]
    grouped: Dict[int, List[DayReading]] = {}
    for reading in days:
        grouped.setdefault(reading.day, []).append(reading)

    outside = sorted(d for d in grouped if not 1 <= d <= last_day)
    inside = sorted(d for d in grouped if 1 <= d <= last_day)

    understood: Dict[int, DayReading] = {}
    unclear: List[int] = []
    for day in inside:
        readings = grouped[day]
        if len(readings) == 1 and is_understood(readings[0]):
            understood[day] = readings[0]
        else:
            unclear.append(day)

    missing: List[int] = []
    if inside:
        missing = [d for d in range(inside[0], inside[-1] + 1) if d not in grouped]
    return Analysis(understood, unclear, missing, outside)


def to_entry(reading: DayReading, year: int, month: int) -> Entry:
    day = date(year, month, reading.day)
    if reading.kind == "shift":
        return Entry.shift(day, reading.start, reading.end)
    return Entry.off(day, normalize_label(reading.off_type or ""))
