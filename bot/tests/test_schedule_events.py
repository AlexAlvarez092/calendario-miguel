import json
from datetime import date, time

from calendario_bot.events import Entry, EventStore
from calendario_bot.schedule import DayReading, analyze, is_understood


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
    assert is_understood(shift(1, "10-18 HT", time(10), time(18), ["HT"]))


def test_not_understood_cases():
    assert not is_understood(shift(1, "10-18 HT", time(10), time(18)))  # annotation not declared
    assert not is_understood(shift(1, "10-18", time(18), time(10)))  # reversed order
    assert not is_understood(shift(1, "10-18", time(10), time(18), uncertain=True))
    assert not is_understood(DayReading(1, "debido 02-11", "unknown"))
    assert not is_understood(shift(1, "debido 02-11", time(2), time(11)))


def test_non_working_understood():
    assert is_understood(DayReading(1, "DESCANSO", "non_working", off_type="Descanso"))
    assert not is_understood(DayReading(1, "DESCANSO extra", "non_working", off_type="Descanso"))


def d(day, month=11):
    return date(2026, month, day)


def test_analyze_classifies_days():
    days = [
        shift(2, "10-18", time(10), time(18)),
        DayReading(3, "???", "unknown"),
        shift(5, "10-18", time(10), time(18)),
        shift(5, "10-18", time(10), time(18)),  # duplicate
        shift(7, "10-18", time(10), time(18)),
    ]
    result = analyze(days, 2026, 11)
    assert sorted(result.understood) == [d(2), d(7)]
    assert result.unclear == [d(3), d(5)]
    assert result.missing == [d(4), d(6)]
    assert result.raw[d(3)] == "???"


def test_analyze_does_not_assume_whole_month():
    days = [shift(n, "10-18", time(10), time(18)) for n in range(12, 16)]
    result = analyze(days, 2026, 10)
    assert sorted(result.understood) == [d(12, 10), d(13, 10), d(14, 10), d(15, 10)]
    assert result.missing == [] and result.error is None


def test_analyze_crosses_month_and_reports_gaps():
    days = [shift(n, "10-18", time(10), time(18)) for n in (29, 30, 1, 3)]
    result = analyze(days, 2026, 11)
    assert sorted(result.understood) == [d(29), d(30), d(1, 12), d(3, 12)]
    assert result.missing == [d(2, 12)]
    last_day_missing = analyze([shift(29, "10-18", time(10), time(18)), shift(1, "10-18", time(10), time(18))], 2026, 11)
    assert last_day_missing.missing == [d(30)]


def test_analyze_year_rollover():
    days = [shift(n, "10-18", time(10), time(18)) for n in (30, 31, 1)]
    result = analyze(days, 2026, 12)
    assert date(2027, 1, 1) in result.understood


def test_analyze_incoherent_order_is_an_error():
    assert analyze([shift(10, "10-18", time(10), time(18)), shift(5, "10-18", time(10), time(18))], 2026, 11).error
    assert analyze([shift(31, "10-18", time(10), time(18))], 2026, 11).error  # November has 30 days


def test_pedido_takes_precedence_over_shift():
    result = analyze([shift(3, "10-18 PEDIDO", time(10), time(18))], 2026, 10)
    reading = result.understood[d(3, 10)]
    assert reading.kind == "non_working" and reading.off_type == "Pedido"
    assert result.unclear == []
