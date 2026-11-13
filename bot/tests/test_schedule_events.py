import json
from datetime import date, time

from calendario_bot.events import Entry, EventStore
from calendario_bot.schedule import DayReading, analyze, is_understood, parse_day_answer, parse_month


def shift(day, raw, start, end, ignored=(), uncertain=False):
    return DayReading(day, raw, "shift", start, end, ignored=list(ignored), uncertain=uncertain)


def test_entry_json_shift_crossing_midnight():
    item = Entry.shift(date(2026, 11, 3), time(18, 0), time(2, 0)).to_json()
    assert item == {
        "id": "2026-11-03",
        "title": "Turno 18:00-02:00",
        "start": "2026-11-03T18:00",
        "end": "2026-11-04T02:00",
    }
    assert Entry.from_json(item) == Entry.shift(date(2026, 11, 3), time(18, 0), time(2, 0))


def test_entry_json_non_working():
    item = Entry.off(date(2026, 11, 5), "Descanso").to_json()
    assert item == {"id": "2026-11-05", "title": "Descanso", "start": "2026-11-05"}
    assert Entry.from_json(item) == Entry.off(date(2026, 11, 5), "Descanso")


def test_store_replaces_by_day_and_sorts(tmp_path):
    store = EventStore(tmp_path / "data" / "events.json")
    store.apply([Entry.off(date(2026, 11, 2), "Descanso"), Entry.shift(date(2026, 11, 1), time(10), time(18))])
    store.apply([Entry.shift(date(2026, 11, 2), time(9), time(17))])
    items = json.loads(store.path.read_text(encoding="utf-8"))
    assert [i["id"] for i in items] == ["2026-11-01", "2026-11-02"]
    assert items[1]["title"] == "Turno 09:00-17:00"


def test_existing_events_file_round_trips():
    path = __import__("pathlib").Path(__file__).resolve().parents[2] / "data" / "events.json"
    original = path.read_text(encoding="utf-8")
    store = EventStore(path)
    assert [e.to_json() for e in (store.load()[d] for d in sorted(store.load()))] == json.loads(original)


def test_understood_shift_and_ignored_annotation():
    assert is_understood(shift(1, "10-18", time(10), time(18)))
    assert is_understood(shift(1, "10-18 PEDIDO", time(10), time(18), ["PEDIDO"]))


def test_not_understood_cases():
    assert not is_understood(shift(1, "10-18 PEDIDO", time(10), time(18)))  # annotation not declared
    assert not is_understood(shift(1, "10-18", time(18), time(10)))  # reversed order
    assert not is_understood(shift(1, "10-18", time(10), time(18), uncertain=True))
    assert not is_understood(DayReading(1, "debido 02-11", "unknown"))
    assert not is_understood(shift(1, "debido 02-11", time(2), time(11)))


def test_non_working_understood():
    assert is_understood(DayReading(1, "DESCANSO", "non_working", off_type="Descanso"))
    assert not is_understood(DayReading(1, "DESCANSO extra", "non_working", off_type="Descanso"))


def test_analyze_classifies_days():
    days = [
        shift(2, "10-18", time(10), time(18)),
        DayReading(3, "???", "unknown"),
        shift(5, "10-18", time(10), time(18)),
        shift(5, "10-18", time(10), time(18)),  # duplicate
        shift(7, "10-18", time(10), time(18)),
        shift(31, "10-18", time(10), time(18)),  # November has 30 days
    ]
    result = analyze(days, 2026, 11)
    assert sorted(result.understood) == [2, 7]
    assert result.unclear == [3, 5]
    assert result.missing == [4, 6]
    assert result.outside == [31]


def test_parse_answers():
    assert parse_month("11/2026") == (2026, 11)
    assert parse_month("13/2026") is None
    assert parse_day_answer("descanso", date(2026, 11, 1)) == Entry.off(date(2026, 11, 1), "Descanso")
    assert parse_day_answer("10-18", date(2026, 11, 1)) == Entry.shift(date(2026, 11, 1), time(10), time(18))
    assert parse_day_answer("hola", date(2026, 11, 1)) is None
