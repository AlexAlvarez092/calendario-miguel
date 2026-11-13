"""Events and their storage in data/events.json (ADR 0008)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class Entry:
    """The event of one day: a shift (start and end) or a non-working day (label)."""

    day: date
    start: Optional[time] = None
    end: Optional[time] = None
    label: Optional[str] = None

    @staticmethod
    def shift(day: date, start: time, end: time) -> "Entry":
        return Entry(day=day, start=start, end=end)

    @staticmethod
    def off(day: date, label: str) -> "Entry":
        return Entry(day=day, label=label)

    @property
    def is_shift(self) -> bool:
        return self.start is not None

    @property
    def title(self) -> str:
        if self.is_shift:
            return f"Turno {self.start:%H:%M}-{self.end:%H:%M}"
        return self.label or ""

    def to_json(self) -> dict:
        data = {"id": self.day.isoformat(), "title": self.title}
        if self.is_shift:
            start = datetime.combine(self.day, self.start)
            end = datetime.combine(self.day, self.end)
            if end <= start:
                end += timedelta(days=1)
            data["start"] = start.strftime("%Y-%m-%dT%H:%M")
            data["end"] = end.strftime("%Y-%m-%dT%H:%M")
        else:
            data["start"] = self.day.isoformat()
        return data

    @staticmethod
    def from_json(item: dict) -> "Entry":
        start_raw = item["start"]
        if "T" in start_raw:
            start = datetime.strptime(start_raw, "%Y-%m-%dT%H:%M")
            end = datetime.strptime(item["end"], "%Y-%m-%dT%H:%M")
            return Entry.shift(start.date(), start.time(), end.time())
        return Entry.off(date.fromisoformat(start_raw), item["title"])


class EventStore:
    """Reads and writes the events file. The file is read on every call because
    the repository can change underneath the bot (ADR 0009)."""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> Dict[date, Entry]:
        if not self.path.exists():
            return {}
        items = json.loads(self.path.read_text(encoding="utf-8"))
        entries = [Entry.from_json(item) for item in items]
        return {entry.day: entry for entry in entries}

    def apply(self, entries: Iterable[Entry]) -> None:
        """Create or replace the event of each entry's day."""
        current = self.load()
        for entry in entries:
            current[entry.day] = entry
        self._write(current)

    def _write(self, entries: Dict[date, Entry]) -> None:
        ordered = [entries[day].to_json() for day in sorted(entries)]
        text = json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".json.tmp")
        temp.write_text(text, encoding="utf-8")
        os.replace(temp, self.path)
