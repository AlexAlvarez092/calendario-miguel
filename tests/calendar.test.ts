import { describe, expect, it } from "vitest";
import { generateCalendarIcs, parseEvents } from "../src/calendar.js";

describe("calendar", () => {
  it("generates a valid empty calendar", () => {
    const ics = generateCalendarIcs([]);
    expect(ics).toContain("BEGIN:VCALENDAR");
    expect(ics).not.toContain("BEGIN:VEVENT");
  });

  it("generates timed and all-day events with stable UIDs", () => {
    const events = parseEvents([
      { id: "a", title: "Timed", start: "2026-12-01T18:30" },
      { id: "b", title: "All day", start: "2026-12-02" },
    ]);
    const ics = generateCalendarIcs(events);

    expect(ics).toContain("UID:a");
    expect(ics).toMatch(/DTSTART;TZID=Europe\/Madrid:20261201T183000/);
    expect(ics).toMatch(/DTSTART;VALUE=DATE:20261202/);
  });

  it("generates a shift crossing midnight and an all-day non-working event", () => {
    const events = parseEvents([
      { id: "2026-12-01", title: "Turno 18:00-02:00", start: "2026-12-01T18:00", end: "2026-12-02T02:00" },
      { id: "2026-12-02", title: "Descanso", start: "2026-12-02" },
    ]);
    const ics = generateCalendarIcs(events);

    expect(ics).toContain("UID:2026-12-01");
    expect(ics).toMatch(/DTEND;TZID=Europe\/Madrid:20261202T020000/);
    expect(ics).toContain("SUMMARY:Descanso");
    expect(ics).toMatch(/DTSTART;VALUE=DATE:20261202/);
  });

  it("rejects duplicate ids and invalid dates", () => {
    const base = { id: "a", title: "T", start: "2026-12-01" };
    expect(() => parseEvents([base, base])).toThrow(/Duplicate/);
    expect(() => parseEvents([{ ...base, start: "nope" }])).toThrow(/Invalid/);
  });
});
