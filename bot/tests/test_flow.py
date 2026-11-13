from datetime import date, time

from calendar_bot.events import Entry, EventStore
from calendar_bot.flow import Flow
from calendar_bot.gemini import ReadingError
from calendar_bot.schedule import DayReading, ReadResult

TODAY = date(2026, 11, 13)


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
    return Flow(store, publisher, reader, today=lambda: TODAY), store, publisher


def shift(day, start=10, end=18):
    return DayReading(day, f"{start}-{end}", "shift", time(start), time(end))


def button(reply, label):
    return next(data for row in reply.rows for text, data in row if text == label)


async def press(flow, reply, label):
    """Press a button and return the first reply."""
    return (await flow.handle_callback(button(reply, label)))[0]


async def pick_shift(flow, kind_reply, start, end):
    reply = await press(flow, kind_reply, "Turno")
    for hour in (start, end):
        reply = await press(flow, reply, "%02d" % hour)
    return reply


async def test_photo_happy_path_confirm_and_publish(tmp_path):
    flow, store, publisher = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(1), shift(2)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert store.load() == {}  # nothing is written before confirming
    out = await flow.handle_callback(button(replies[-1], "Confirmar"))
    assert len(store.load()) == 2 and len(publisher.messages) == 1
    assert out[0].text.startswith("Hecho")


async def test_photo_not_starting_on_day_one(tmp_path):
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(10, 2026, [shift(12), shift(13)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "12/10/2026" in replies[-1].text and "01/10/2026" not in replies[-1].text
    assert not any("Falta" in r.text for r in replies)


async def test_reject_changes_nothing(tmp_path):
    flow, store, publisher = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(1)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    await flow.handle_callback(button(replies[-1], "Rechazar"))
    assert store.load() == {} and publisher.messages == []


async def test_summary_only_lists_changes(tmp_path):
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(1), shift(2, 9, 17)])))
    store.apply([Entry.shift(date(2026, 11, 1), time(10), time(18))])
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "02/11/2026" in replies[-1].text and "01/11/2026" not in replies[-1].text


async def test_clarification_of_unclear_and_missing_days(tmp_path):
    days = [shift(1), DayReading(2, "debido 02-11", "unknown"), shift(4)]
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, days)))
    reply = (await flow.start_photo(b"x", "image/jpeg"))[0]
    assert "02/11/2026" in reply.text and "debido 02-11" in reply.text
    reply = await pick_shift(flow, reply, 9, 17)
    assert "03/11/2026" in reply.text  # the missing day is asked next
    kind = await press(flow, reply, "Día no laborable")
    summary = await press(flow, kind, "Descanso")
    assert "Turno 09:00-17:00" in summary.text and "Descanso" in summary.text
    await flow.handle_callback(button(summary, "Confirmar"))
    assert len(store.load()) == 4


async def test_missing_month_is_asked_with_buttons(tmp_path):
    flow, _, _ = make_flow(tmp_path, FakeReader(ReadResult(None, None, [shift(12)])))
    reply = (await flow.start_photo(b"x", "image/jpeg"))[0]
    out = await press(flow, reply, "Octubre 2026")
    assert "12/10/2026" in out.text


async def test_incoherent_days_end_the_interaction(tmp_path):
    flow, _, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(10), shift(5)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "No he podido ordenar" in replies[0].text and flow.current is None


async def test_reading_error_ends_interaction(tmp_path):
    flow, _, _ = make_flow(tmp_path, FakeReader(error=ReadingError("El servicio de IA no responde ahora mismo.")))
    replies = await flow.start_photo(b"x", "image/jpeg")
    assert "no responde" in replies[0].text and flow.current is None


async def test_stale_callback_and_cancel_button(tmp_path):
    flow, store, _ = make_flow(tmp_path, FakeReader(ReadResult(11, 2026, [shift(1)])))
    replies = await flow.start_photo(b"x", "image/jpeg")
    confirm = button(replies[-1], "Confirmar")
    new = flow.start_command("add")  # replaces the photo interaction
    assert await flow.handle_callback(confirm) == []
    assert store.load() == {}
    out = await flow.handle_callback(button(new, "Cancelar"))
    assert "Cancelado" in out[0].text and flow.current is None


async def test_menu_starts_commands(tmp_path):
    flow, _, _ = make_flow(tmp_path)
    out = await flow.handle_callback(button(flow.menu(), "Añadir evento"))
    assert "¿Qué día?" in out[0].text and flow.current.kind == "add"


async def test_date_picker_shows_month_and_navigates(tmp_path):
    flow, _, _ = make_flow(tmp_path)
    picker = flow.start_command("add")
    assert "Noviembre 2026" in [text for row in picker.rows for text, _ in row]
    nxt = await press(flow, picker, "›")
    assert "Diciembre 2026" in [text for row in nxt.rows for text, _ in row]


async def test_add_shift_with_replace_question(tmp_path):
    flow, store, _ = make_flow(tmp_path)
    store.apply([Entry.off(date(2026, 11, 5), "Descanso")])
    picker = flow.start_command("add")
    question = await press(flow, picker, "5")
    assert "reemplazar" in question.text
    kind = await press(flow, question, "Sí, reemplazar")
    summary = await pick_shift(flow, kind, 18, 2)
    assert "Turno 18:00-02:00" in summary.text and "antes: Descanso" in summary.text
    await flow.handle_callback(button(summary, "Confirmar"))
    assert store.load()[date(2026, 11, 5)] == Entry.shift(date(2026, 11, 5), time(18), time(2))


async def test_declining_replacement_leaves_event(tmp_path):
    flow, store, publisher = make_flow(tmp_path)
    store.apply([Entry.off(date(2026, 11, 5), "Descanso")])
    question = await press(flow, flow.start_command("add"), "5")
    await press(flow, question, "No")
    assert flow.current is None and publisher.messages == []


async def test_end_time_equal_to_start_is_asked_again(tmp_path):
    flow, _, _ = make_flow(tmp_path)
    kind = await press(flow, flow.start_command("add"), "10")
    reply = await press(flow, kind, "Turno")
    reply = await press(flow, reply, "08")
    reply = await press(flow, reply, "08")
    assert "igual" in reply.text and flow.current.step == "hour"


async def test_non_working_type_by_button_or_free_text(tmp_path):
    flow, store, _ = make_flow(tmp_path)
    kind = await press(flow, flow.start_command("add"), "10")
    types = await press(flow, kind, "Día no laborable")
    summary = await press(flow, types, "Vacaciones")
    await flow.handle_callback(button(summary, "Confirmar"))
    assert store.load()[date(2026, 11, 10)].title == "Vacaciones"

    kind = await press(flow, flow.start_command("add"), "11")
    await press(flow, kind, "Día no laborable")
    out = await flow.handle_text("curso de formación")
    assert "Curso de formación" in out[0].text


async def test_modify_without_event_points_to_add(tmp_path):
    flow, _, _ = make_flow(tmp_path)
    out = await press(flow, flow.start_command("modify"), "10")
    assert "Añadir evento" in out.text and flow.current is None
