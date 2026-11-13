import ical from "ical-generator";
import { DateTime } from "luxon";

export const TIMEZONE = "Europe/Madrid";

export interface EventInput {
  /** Stable identifier. It is the date of the event (`YYYY-MM-DD`), see ADR 0008. */
  id: string;
  title: string;
  /** `YYYY-MM-DD` for all-day events or `YYYY-MM-DDTHH:mm` (Europe/Madrid) for timed ones. */
  start: string;
  /** Same format as `start`. Optional. */
  end?: string;
  location?: string;
  description?: string;
}

export function parseEvents(raw: unknown): EventInput[] {
  if (!Array.isArray(raw)) {
    throw new Error("events.json must contain an array.");
  }

  const seen = new Set<string>();

  return raw.map((item, index) => {
    const event = item as Partial<EventInput>;

    if (!event.id || !event.title || !event.start) {
      throw new Error(`Event #${index} requires id, title and start.`);
    }

    if (seen.has(event.id)) {
      throw new Error(`Duplicate event id: ${event.id}`);
    }

    seen.add(event.id);
    parseDate(event.start, event.id);
    if (event.end) parseDate(event.end, event.id);

    return event as EventInput;
  });
}

export function generateCalendarIcs(events: EventInput[]): string {
  const calendar = ical({
    name: "Calendario Miguel",
    timezone: TIMEZONE,
    prodId: { company: "calendario-miguel", product: "calendario-miguel" },
  });

  for (const event of events) {
    calendar.createEvent({
      id: event.id,
      start: parseDate(event.start, event.id),
      end: event.end ? parseDate(event.end, event.id) : undefined,
      allDay: isAllDay(event.start),
      summary: event.title,
      location: event.location,
      description: event.description,
      timezone: TIMEZONE,
    });
  }

  return calendar.toString();
}

function isAllDay(value: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(value);
}

function parseDate(value: string, id: string): DateTime {
  const parsed = DateTime.fromISO(value, { zone: TIMEZONE });

  if (!parsed.isValid) {
    throw new Error(`Invalid date "${value}" in event ${id}.`);
  }

  return parsed;
}
