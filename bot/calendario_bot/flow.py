"""Conversation logic of the bot, independent of Telegram (FR-004, FR-005, FR-007, FR-020, FR-022, FR-025).

All user-facing text is Spanish (NFR-006).
"""
from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from .events import Entry, EventStore
from .gemini import ReadingError
from .schedule import (
    NON_WORKING_TYPES,
    analyze,
    normalize_label,
    parse_date,
    parse_day_answer,
    parse_month,
    parse_time,
    to_entry,
)

logger = logging.getLogger(__name__)

ANSWER_HELP = "Escribe un horario (por ejemplo 10-18) o Descanso, Vacaciones, Festivo o Compensatorio."


@dataclass
class Reply:
    text: str
    buttons: List[Tuple[str, str]] = field(default_factory=list)  # (label, callback data)


@dataclass
class Interaction:
    id: int
    kind: str  # "photo", "add" or "modify"
    step: str
    data: Dict[str, Any] = field(default_factory=dict)


class Flow:
    """Holds the single interaction in progress, in memory only (FR-025)."""

    def __init__(self, store: EventStore, publisher, reader):
        self._store = store
        self._publisher = publisher
        self._reader = reader
        self._counter = 0
        self.current: Optional[Interaction] = None

    # Starting and cancelling interactions

    def _begin(self, kind: str, step: str) -> Interaction:
        self._counter += 1
        self.current = Interaction(self._counter, kind, step)
        return self.current

    def _cb(self, it: Interaction, action: str, arg: str = "") -> str:
        return f"{it.id}:{action}:{arg}" if arg else f"{it.id}:{action}"

    def cancel(self) -> Reply:
        if self.current is None:
            return Reply("No hay nada que cancelar.")
        self.current = None
        return Reply("Cancelado. No se ha modificado nada.")

    def start_command(self, kind: str) -> Reply:
        self._begin(kind, "date")
        return Reply("Dime el día con el formato dd/mm/yyyy (por ejemplo 15/11/2026).")

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
        it.data.update(
            month=result.month, year=result.year, days=result.days, fixed={}, ignore_outside=False
        )
        return self._advance_photo(it)

    def _fail_photo(self, it: Interaction, text: str) -> List[Reply]:
        if self.current is not it:
            return []
        self.current = None
        return [Reply(text)]

    # Photo flow

    def _advance_photo(self, it: Interaction) -> List[Reply]:
        data = it.data
        if not data["days"]:
            self.current = None
            return [Reply("No he encontrado ninguna fila de Miguel en la foto.")]
        if data["month"] is None or data["year"] is None:
            it.step = "month"
            return [Reply("No he podido identificar el mes y el año de la foto. Indícalos con el formato mm/yyyy (por ejemplo 11/2026).")]

        year, month = data["year"], data["month"]
        analysis = analyze(data["days"], year, month)
        if analysis.outside and not data["ignore_outside"]:
            it.step = "outside"
            days = ", ".join(str(d) for d in analysis.outside)
            return [
                Reply(
                    f"En la foto aparecen días que no existen en {month:02d}/{year}: {days}. ¿Qué hago?",
                    [("Ignorar esos días", self._cb(it, "ignore")), ("Cambiar mes y año", self._cb(it, "month"))],
                )
            ]

        pending = sorted((set(analysis.unclear) | set(analysis.missing)) - set(data["fixed"]))
        if pending:
            return [self._ask_day(it, pending, analysis.missing)]

        entries = [to_entry(reading, year, month) for reading in analysis.understood.values()]
        entries += [dataclasses.replace(entry, day=date(year, month, day)) for day, entry in data["fixed"].items()]
        return [self._summary(it, entries)]

    def _ask_day(self, it: Interaction, pending: List[int], missing: List[int]) -> Reply:
        day = pending[0]
        it.step = "clarify"
        it.data["asking"] = day
        intro = ""
        if not it.data.get("intro_done"):
            it.data["intro_done"] = True
            intro = "Hay días que no tengo claros: " + ", ".join(str(d) for d in pending) + ".\n"
        if day in missing:
            what = f"Falta el día {day} en la fila de Miguel."
        else:
            raw = next(r.raw_text for r in it.data["days"] if r.day == day)
            what = f"No entiendo la celda del día {day} (texto leído: «{raw}»)."
        return Reply(f"{intro}{what} ¿Qué turno tiene? {ANSWER_HELP}")

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
        return Reply(text, [("Confirmar", self._cb(it, "yes")), ("Rechazar", self._cb(it, "no"))])

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

    # Text answers

    async def handle_text(self, text: str) -> List[Reply]:
        it = self.current
        if it is None:
            return [Reply("Envíame la foto del cuadrante o usa /add o /modify.")]
        handler = getattr(self, f"_text_{it.step}", None)
        if handler is None:
            if it.step == "reading":
                return [Reply("Sigo leyendo la foto. Usa /cancel si quieres cancelarla.")]
            return [Reply("Usa los botones del mensaje anterior o /cancel.")]
        return handler(it, text)

    def _text_month(self, it: Interaction, text: str) -> List[Reply]:
        parsed = parse_month(text)
        if parsed is None:
            return [Reply("No entiendo ese mes. Usa el formato mm/yyyy (por ejemplo 11/2026).")]
        it.data["year"], it.data["month"] = parsed
        return self._advance_photo(it)

    def _text_clarify(self, it: Interaction, text: str) -> List[Reply]:
        day = it.data["asking"]
        entry = parse_day_answer(text, date(it.data["year"], it.data["month"], day))
        if entry is None:
            return [Reply(f"No entiendo esa respuesta. {ANSWER_HELP}")]
        it.data["fixed"][day] = entry
        return self._advance_photo(it)

    def _text_date(self, it: Interaction, text: str) -> List[Reply]:
        day = parse_date(text)
        if day is None:
            return [Reply("No entiendo esa fecha. Usa el formato dd/mm/yyyy (por ejemplo 15/11/2026).")]
        existing = self._store.load().get(day)
        it.data["day"] = day
        if it.kind == "modify" and existing is None:
            self.current = None
            return [Reply("Ese día no tiene evento. Usa /add para añadirlo.")]
        if it.kind == "add" and existing is not None:
            it.step = "replace"
            return [
                Reply(
                    f"El {day:%d/%m/%Y} ya tiene el evento «{existing.title}». ¿Quieres reemplazarlo?",
                    [("Sí, reemplazar", self._cb(it, "yes")), ("No", self._cb(it, "no"))],
                )
            ]
        return [self._ask_kind(it)]

    def _ask_kind(self, it: Interaction) -> Reply:
        it.step = "kind"
        return Reply(
            "¿Es un turno o un día no laborable?",
            [("Turno", self._cb(it, "shift")), ("Día no laborable", self._cb(it, "off"))],
        )

    def _text_start(self, it: Interaction, text: str) -> List[Reply]:
        start = parse_time(text)
        if start is None:
            return [Reply("No entiendo esa hora. Usa el formato HH:MM (por ejemplo 18:00).")]
        it.data["start"] = start
        it.step = "end"
        return [Reply("¿A qué hora termina? (por ejemplo 02:00)")]

    def _text_end(self, it: Interaction, text: str) -> List[Reply]:
        end = parse_time(text)
        if end is None or end == it.data["start"]:
            return [Reply("No entiendo esa hora. Usa el formato HH:MM (por ejemplo 02:00) y distinta de la de inicio.")]
        return [self._summary(it, [Entry.shift(it.data["day"], it.data["start"], end)])]

    def _text_type(self, it: Interaction, text: str) -> List[Reply]:
        label = normalize_label(text)
        if not label:
            return [Reply("Escribe el tipo de día no laborable.")]
        return [self._summary(it, [Entry.off(it.data["day"], label)])]

    # Button answers

    async def handle_callback(self, data: str) -> List[Reply]:
        parts = data.split(":", 2)
        it = self.current
        if it is None or parts[0] != str(it.id):
            return []  # answer to a cancelled interaction (FR-025)
        action = parts[1]
        arg = parts[2] if len(parts) > 2 else ""

        if it.step == "confirm":
            if action == "yes":
                return await self._apply(it)
            if action == "no":
                self.current = None
                return [Reply("Rechazado. No se ha modificado nada.")]
        elif it.step == "outside":
            if action == "ignore":
                it.data["ignore_outside"] = True
                return self._advance_photo(it)
            if action == "month":
                it.step = "month"
                return [Reply("Indica el mes y el año correctos con el formato mm/yyyy (por ejemplo 11/2026).")]
        elif it.step == "replace":
            if action == "yes":
                return [self._ask_kind(it)]
            if action == "no":
                self.current = None
                return [Reply("Vale, no cambio nada.")]
        elif it.step == "kind":
            if action == "shift":
                it.step = "start"
                return [Reply("¿A qué hora empieza? (por ejemplo 18:00)")]
            if action == "off":
                it.step = "type"
                buttons = [(name, self._cb(it, "type", name)) for name in NON_WORKING_TYPES]
                return [Reply("¿Qué tipo de día no laborable es? Elige uno o escríbelo.", buttons)]
        elif it.step == "type" and action == "type" and arg in NON_WORKING_TYPES:
            return [self._summary(it, [Entry.off(it.data["day"], arg)])]
        return []
