"""Conversation logic of the bot, independent of Telegram (FR-004, FR-005, FR-007, FR-020, FR-022, FR-025).

Miguel answers with buttons wherever possible. All user-facing text is Spanish (NFR-006).
"""
from __future__ import annotations

import calendar
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any, Callable, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from .events import Entry, EventStore
from .gemini import ReadingError
from .schedule import NON_WORKING_TYPES, analyze, normalize_label, to_entry

logger = logging.getLogger(__name__)

MONTH_NAMES = (
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)
WEEKDAYS = ("L", "M", "X", "J", "V", "S", "D")
MINUTES = (0, 15, 30, 45)
MENU_PREFIX = "m"

Button = Tuple[str, str]  # (label, callback data)


@dataclass
class Reply:
    text: str
    rows: List[List[Button]] = field(default_factory=list)


@dataclass
class Interaction:
    id: int
    kind: str  # "photo", "add" or "modify"
    step: str
    data: Dict[str, Any] = field(default_factory=dict)


def _today() -> date:
    return datetime.now(ZoneInfo("Europe/Madrid")).date()


def _month_label(year: int, month: int) -> str:
    return f"{MONTH_NAMES[month - 1]} {year}"


def _shift_month(year: int, month: int, delta: int) -> Tuple[int, int]:
    index = year * 12 + (month - 1) + delta
    return index // 12, index % 12 + 1


class Flow:
    """Holds the single interaction in progress, in memory only (FR-025)."""

    def __init__(self, store: EventStore, publisher, reader, today: Callable[[], date] = _today):
        self._store = store
        self._publisher = publisher
        self._reader = reader
        self._today = today
        self._counter = 0
        self.current: Optional[Interaction] = None

    # Interactions

    def _begin(self, kind: str, step: str) -> Interaction:
        self._counter += 1
        self.current = Interaction(self._counter, kind, step)
        return self.current

    @staticmethod
    def _cb(it: Interaction, action: str, arg: str = "") -> str:
        return f"{it.id}:{action}:{arg}" if arg else f"{it.id}:{action}"

    def _reply(self, it: Interaction, text: str, rows: List[List[Button]]) -> Reply:
        return Reply(text, rows + [[("Cancelar", self._cb(it, "cancel"))]])

    def cancel(self) -> Reply:
        if self.current is None:
            return Reply("No hay nada que cancelar.")
        self.current = None
        return Reply("Cancelado. No se ha modificado nada.")

    def menu(self) -> Reply:
        return Reply(
            "Hola. Envíame la foto del cuadrante o elige una opción.",
            [[("Añadir evento", f"{MENU_PREFIX}:add")], [("Modificar evento", f"{MENU_PREFIX}:modify")]],
        )

    def start_command(self, kind: str) -> Reply:
        it = self._begin(kind, "date")
        today = self._today()
        return self._date_picker(it, today.year, today.month, "¿Qué día?")

    # Pickers

    def _date_picker(self, it: Interaction, year: int, month: int, text: str) -> Reply:
        it.step = "date"
        previous, following = _shift_month(year, month, -1), _shift_month(year, month, 1)
        rows: List[List[Button]] = [
            [
                ("‹", self._cb(it, "nav", "%d-%02d" % previous)),
                (_month_label(year, month), self._cb(it, "noop")),
                ("›", self._cb(it, "nav", "%d-%02d" % following)),
            ],
            [(name, self._cb(it, "noop")) for name in WEEKDAYS],
        ]
        for week in calendar.Calendar().monthdayscalendar(year, month):
            rows.append(
                [
                    (str(d), self._cb(it, "pick", date(year, month, d).isoformat())) if d else (" ", self._cb(it, "noop"))
                    for d in week
                ]
            )
        return self._reply(it, text, rows)

    def _hour_picker(self, it: Interaction, which: str, text: str) -> Reply:
        it.step = "hour"
        it.data["which"] = which
        buttons = [("%02d" % h, self._cb(it, "hour", str(h))) for h in range(24)]
        return self._reply(it, text, [buttons[i : i + 6] for i in range(0, 24, 6)])

    def _minute_picker(self, it: Interaction) -> Reply:
        it.step = "minute"
        row = [("%02d" % m, self._cb(it, "min", str(m))) for m in MINUTES]
        return self._reply(it, f"Hora: {it.data['hour']:02d}. ¿Y los minutos?", [row])

    def _kind_picker(self, it: Interaction, text: str) -> Reply:
        it.step = "kind"
        return self._reply(
            it, text, [[("Turno", self._cb(it, "shift")), ("Día no laborable", self._cb(it, "off"))]]
        )

    def _type_picker(self, it: Interaction) -> Reply:
        it.step = "type"
        buttons = [(name, self._cb(it, "type", name)) for name in NON_WORKING_TYPES]
        return self._reply(
            it, "¿Qué tipo de día no laborable es? Elige uno o escribe otro.", [buttons[:2], buttons[2:]]
        )

    def _entry_built(self, it: Interaction, entry: Entry) -> List[Reply]:
        if it.kind == "photo":
            it.data["fixed"][entry.day] = entry
            return self._advance_photo(it)
        return [self._summary(it, [entry])]

    # Photo flow

    async def start_photo(self, image: bytes, mime_type: str) -> List[Reply]:
        it = self._begin("photo", "reading")
        try:
            result = await self._reader.read(image, mime_type)
        except ReadingError as error:
            return self._fail_photo(it, f"{error} No he podido procesar la foto. Envíala de nuevo más tarde.")
        except Exception:
            logger.exception("Unexpected error reading the photo")
            return self._fail_photo(it, "Ha ocurrido un error inesperado al procesar la foto.")
        if self.current is not it:
            return []  # cancelled or replaced while reading: discard the result
        it.data.update(month=result.month, year=result.year, days=result.days, fixed={})
        return self._advance_photo(it)

    def _fail_photo(self, it: Interaction, text: str) -> List[Reply]:
        if self.current is not it:
            return []
        self.current = None
        return [Reply(text)]

    def _advance_photo(self, it: Interaction) -> List[Reply]:
        data = it.data
        if not data["days"]:
            self.current = None
            return [Reply("No he encontrado ninguna fila de Miguel en la foto.")]
        if data["month"] is None or data["year"] is None:
            return [self._month_picker(it)]

        analysis = analyze(data["days"], data["year"], data["month"])
        if analysis.error:
            self.current = None
            return [Reply(f"No he podido ordenar los días de la foto: {analysis.error} Envíala de nuevo o usa el menú /start.")]

        pending = sorted((set(analysis.unclear) | set(analysis.missing)) - set(data["fixed"]))
        if pending:
            return [self._ask_day(it, pending, set(analysis.missing), analysis)]

        entries = [to_entry(reading, day) for day, reading in analysis.understood.items()]
        entries += list(data["fixed"].values())
        return [self._summary(it, entries)]

    def _month_picker(self, it: Interaction) -> Reply:
        it.step = "month"
        today = self._today()
        buttons = []
        for delta in (-1, 0, 1):
            year, month = _shift_month(today.year, today.month, delta)
            buttons.append((_month_label(year, month), self._cb(it, "month", "%d-%02d" % (year, month))))
        return self._reply(
            it, "No he podido leer el mes y el año de la foto. ¿De qué mes es el primer día de la foto?", [buttons]
        )

    def _ask_day(self, it: Interaction, pending: List[date], missing: set, analysis) -> Reply:
        day = pending[0]
        it.data["day"] = day
        intro = ""
        if not it.data.get("intro_done"):
            it.data["intro_done"] = True
            intro = "Hay días que no tengo claros: " + ", ".join(f"{d:%d/%m}" for d in pending) + ".\n"
        if day in missing:
            what = f"Falta el día {day:%d/%m/%Y} en la fila de Miguel."
        else:
            what = f"No entiendo la celda del día {day:%d/%m/%Y} (texto leído: «{analysis.raw.get(day, '')}»)."
        return self._kind_picker(it, f"{intro}{what} ¿Qué tiene ese día?")

    # Summary and confirmation (FR-022)

    def _summary(self, it: Interaction, entries: List[Entry]) -> Reply:
        existing = self._store.load()
        changes = sorted((e for e in entries if existing.get(e.day) != e), key=lambda e: e.day)
        if not changes:
            self.current = None
            return Reply("No hay nada que cambiar: el calendario ya tiene esos eventos.")
        it.step = "confirm"
        it.data["changes"] = changes
        lines = []
        for entry in changes:
            before = existing.get(entry.day)
            note = "nuevo" if before is None else f"antes: {before.title}"
            lines.append(f"• {entry.day:%d/%m/%Y}: {entry.title} ({note})")
        text = "Estos son los cambios:\n" + "\n".join(lines) + "\n¿Los aplico?"
        return Reply(text, [[("Confirmar", self._cb(it, "yes")), ("Rechazar", self._cb(it, "no"))]])

    async def _apply(self, it: Interaction) -> List[Reply]:
        changes: List[Entry] = it.data["changes"]
        self.current = None
        self._store.apply(changes)
        try:
            await self._publisher.publish(f"Update events ({len(changes)} changes)")
        except Exception:
            logger.exception("Could not commit the changes")
            return [Reply("He guardado los cambios, pero no he podido prepararlos para publicarlos. Avisa al desarrollador.")]
        return [Reply(f"Hecho. He guardado {len(changes)} cambio(s); se publicarán en el calendario en breve.")]

    # Free text: only the type of a non-working day accepts it

    async def handle_text(self, text: str) -> List[Reply]:
        it = self.current
        if it is None:
            return [Reply("Envíame la foto del cuadrante o pulsa /start para ver el menú.")]
        if it.step == "reading":
            return [Reply("Sigo leyendo la foto. Usa /cancel si quieres cancelarla.")]
        label = normalize_label(text)
        if it.step == "type" and label:
            return self._entry_built(it, Entry.off(it.data["day"], label))
        return [Reply("Usa los botones del mensaje anterior o /cancel.")]

    # Button answers

    async def handle_callback(self, data: str) -> List[Reply]:
        parts = data.split(":", 2)
        action = parts[1] if len(parts) > 1 else ""
        arg = parts[2] if len(parts) > 2 else ""
        if parts[0] == MENU_PREFIX:
            return [self.start_command(action)] if action in ("add", "modify") else []

        it = self.current
        if it is None or parts[0] != str(it.id):
            return []  # answer to a cancelled interaction (FR-025)
        if action == "noop":
            return []
        if action == "cancel":
            return [self.cancel()]
        handler = getattr(self, f"_on_{it.step}", None)
        return await handler(it, action, arg) if handler else []

    async def _on_confirm(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action == "yes":
            return await self._apply(it)
        if action == "no":
            self.current = None
            return [Reply("Rechazado. No se ha modificado nada.")]
        return []

    async def _on_month(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action != "month":
            return []
        year, month = arg.split("-")
        it.data["year"], it.data["month"] = int(year), int(month)
        return self._advance_photo(it)

    async def _on_date(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action == "nav":
            year, month = arg.split("-")
            return [self._date_picker(it, int(year), int(month), "¿Qué día?")]
        if action != "pick":
            return []
        day = date.fromisoformat(arg)
        existing = self._store.load().get(day)
        it.data["day"] = day
        if it.kind == "modify" and existing is None:
            self.current = None
            return [Reply("Ese día no tiene evento. Usa «Añadir evento» del menú /start.")]
        if it.kind == "add" and existing is not None:
            it.step = "replace"
            return [
                self._reply(
                    it,
                    f"El {day:%d/%m/%Y} ya tiene el evento «{existing.title}». ¿Quieres reemplazarlo?",
                    [[("Sí, reemplazar", self._cb(it, "yes")), ("No", self._cb(it, "no"))]],
                )
            ]
        return [self._kind_picker(it, f"{day:%d/%m/%Y}: ¿es un turno o un día no laborable?")]

    async def _on_replace(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action == "yes":
            return [self._kind_picker(it, f"{it.data['day']:%d/%m/%Y}: ¿es un turno o un día no laborable?")]
        if action == "no":
            self.current = None
            return [Reply("Vale, no cambio nada.")]
        return []

    async def _on_kind(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action == "shift":
            return [self._hour_picker(it, "start", "¿A qué hora empieza?")]
        if action == "off":
            return [self._type_picker(it)]
        return []

    async def _on_type(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action == "type" and arg in NON_WORKING_TYPES:
            return self._entry_built(it, Entry.off(it.data["day"], arg))
        return []

    async def _on_hour(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action != "hour":
            return []
        it.data["hour"] = int(arg)
        return [self._minute_picker(it)]

    async def _on_minute(self, it: Interaction, action: str, arg: str) -> List[Reply]:
        if action != "min":
            return []
        chosen = time(it.data["hour"], int(arg))
        if it.data["which"] == "start":
            it.data["start"] = chosen
            return [self._hour_picker(it, "end", f"Empieza a las {chosen:%H:%M}. ¿A qué hora termina?")]
        if chosen == it.data["start"]:
            return [self._hour_picker(it, "end", "El fin no puede ser igual que el inicio. ¿A qué hora termina?")]
        return self._entry_built(it, Entry.shift(it.data["day"], it.data["start"], chosen))
