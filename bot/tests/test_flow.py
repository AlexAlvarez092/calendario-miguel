from datetime import date, time

from calendario_bot.events import Entry, EventStore
from calendario_bot.flow import Flow
from calendario_bot.gemini import ReadingError
from calendario_bot.schedule import DayReading, ReadResult


class FakePublisher:
    def __init__(self):
        self.messages = []

    async def publish(self, message):
        self.messages.append(message)


class FakeReader:
    def __init__(self, result=None, error=None):
        self.result, self.error = result, error

    async def read(self, image, mime_type):
        if self.error:
            raise self.error
        return self.result


def make_flow(tmp_path, reader=None):
    store = EventStore(tmp_path / "events.json")
    publisher = FakePublisher()
    return Flow(store, publisher, reader), store, publisher


def shift(day, start=10, end=18):
    return DayReading(day, f"{start}-{end}", "shift", time(start), time(end))


def button(reply, label):
    return next(data for text, data in reply.buttons if text == label)


async def test_photo_happy_path_confirm_and_publish(tmp_path):
    result = ReadResult(11, 2026, [shift(1), shift(2)])
    flow, store, publisher = make_flow(tmp_path, FakeReader(result))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "Confirmar" in [label for label, _ in replies[-1].buttons]
    assert store.load() == {}  # nothing is written before confirming
    out = await flow.handle_callback(button(replies[-1], "Confirmar"))
    assert len(store.load()) == 2 and len(publisher.messages) == 1
    assert out[0].text.startswith("Hecho")


async def test_reject_changes_nothing(tmp_path):
    flow, store, publisher = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(1)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    await flow.handle_callback(button(replies[-1], "Rechazar"))
    assert store.load() == {} and publisher.messages == []


async def test_summary_only_lists_changes(tmp_path):
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(1), shift(2, 9, 17)])))
    store.apply([Entry.shift(date(2026, 11, 1), time(10), time(18))])
    replies = await flow.start_photo(b"x", "image/jpeg")
    text = replies[-1].text
    assert "02/11/2026" in text and "01/11/2026" not in text and "antes" not in text.split("02/11")[0]


async def test_clarification_then_missing_day_and_invalid_answer(tmp_path):
    days = [shift(1), DayReading(2, "debido 02-11", "unknown"), shift(4)]
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, days)))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "día 2" in replies[0].text
    again = await flow.handle_text("no sé")
    assert "No entiendo" in again[0].text and flow.current.step == "clarify"
    nxt = await flow.handle_text("Descanso")
    assert "día 3" in nxt[0].text
    last = await flow.handle_text("10-18")
    assert last[0].buttons


async def test_missing_month_is_asked(tmp_path):
    flow, _, _ = make_flow(tmp_path, FakeReader(ReadResult(None, None, [shift(1)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "mm/yyyy" in replies[0].text
    out = await flow.handle_text("11/2026")
    assert out[0].buttons


async def test_days_outside_month_can_be_ignored(tmp_path):
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(30), shift(31)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    out = await flow.handle_callback(button(replies[0], "Ignorar esos días"))
    assert "30/11/2026" in out[0].text and "31" not in out[0].text


async def test_reading_error_ends_interaction(tmp_path):
    flow, _, _ = make_flow(tmp_path, FakeReader(error=ReadingError("El servicio de IA no responde ahora mismo.")))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "no responde" in replies[0].text and flow.current is None


async def test_stale_callback_and_cancel(tmp_path):
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(1)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    confirm = button(replies[-1], "Confirmar")
    flow.start_command("add")  # replaces the photo interaction
    assert await flow.handle_callback(confirm) == []
    assert store.load() == {}
    assert "Cancelado" in flow.cancel().text and flow.current is None


async def test_add_shift_and_replace_question(tmp_path):
    flow, store, _ = make_flow(tmp_path)
    store.apply([Entry.off(date(2026, 11, 5), "Descanso")])
    flow.start_command("add")
    assert "formato" in (await flow.handle_text("5-11"))[0].text
    q = (await flow.handle_text("05/11/2026"))[0]
    assert "reemplazar" in q.text
    kind = (await flow.handle_callback(button(q, "Sí, reemplazar")))[0]
    await flow.handle_callback(button(kind, "Turno"))
    await flow.handle_text("18")
    summary = (await flow.handle_text("02:00"))[0]
    assert "Turno 18:00-02:00" in summary.text and "antes: Descanso" in summary.text
    await flow.handle_callback(button(summary, "Confirmar"))
    assert store.load()[date(2026, 11, 5)] == Entry.shift(date(2026, 11, 5), time(18), time(2))


async def test_add_non_working_with_button(tmp_path):
    flow, store, _ = make_flow(tmp_path)
    flow.start_command("add")
    kind = (await flow.handle_text("10/11/2026"))[0]
    types = (await flow.handle_callback(button(kind, "Día no laborable")))[0]
    summary = (await flow.handle_callback(button(types, "Vacaciones")))[0]
    await flow.handle_callback(button(summary, "Confirmar"))
    assert store.load()[date(2026, 11, 10)].title == "Vacaciones"


async def test_modify_without_event_points_to_add(tmp_path):
    flow, _, _ = make_flow(tmp_path)
    flow.start_command("modify")
    out = await flow.handle_text("10/11/2026")
    assert "/add" in out[0].text and flow.current is None
