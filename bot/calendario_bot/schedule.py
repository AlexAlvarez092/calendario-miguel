"""Readings of the schedule photo and their validation (FR-004)."""
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


def normalize_label(text: str) -> str:
    return text.strip().capitalize()


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
    understood: Dict[date, DayReading]
    unclear: List[date]
    missing: List[date]
    error: Optional[str] = None
    raw: Dict[date, str] = field(default_factory=dict)  # literal text of the unclear days


def _days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def _next_month(year: int, month: int) -> Tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def analyze(days: List[DayReading], year: int, month: int) -> Analysis:
    """Give a date to each day read and classify it. The photo covers consecutive days
    in reading order, starting in the given month; the month changes when the day number
    goes down after the end of a month. The photo is not assumed to cover a whole month."""
    grouped: Dict[date, List[DayReading]] = {}
    missing: List[date] = []
    previous: Optional[int] = None
    for reading in days:
        last = _days_in_month(year, month)
        if previous is not None and reading.day < previous:
            if previous < 28 or reading.day > 7:
                return Analysis({}, [], [], f"El día {reading.day} aparece después del {previous}.")
            missing += [date(year, month, d) for d in range(previous + 1, last + 1)]
            year, month = _next_month(year, month)
            previous = 0
            last = _days_in_month(year, month)
        if not 1 <= reading.day <= last:
            return Analysis({}, [], [], f"El día {reading.day} no existe en {month:02d}/{year}.")
        if previous is not None and reading.day > previous + 1:
            missing += [date(year, month, d) for d in range(previous + 1, reading.day)]
        grouped.setdefault(date(year, month, reading.day), []).append(reading)
        previous = reading.day

    understood: Dict[date, DayReading] = {}
    unclear: List[date] = []
    raw: Dict[date, str] = {}
    for day, readings in sorted(grouped.items()):
        if len(readings) == 1 and is_understood(readings[0]):
            understood[day] = readings[0]
        else:
            unclear.append(day)
            raw[day] = " / ".join(r.raw_text for r in readings)
    return Analysis(understood, unclear, sorted(missing), raw=raw)


def to_entry(reading: DayReading, day: date) -> Entry:
    if reading.kind == "shift":
        return Entry.shift(day, reading.start, reading.end)
    return Entry.off(day, normalize_label(reading.off_type or ""))
