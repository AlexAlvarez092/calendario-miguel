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

  it("rejects duplicate ids and invalid dates", () => {
    const base = { id: "a", title: "T", start: "2026-12-01" };
    expect(() => parseEvents([base, base])).toThrow(/Duplicate/);
    expect(() => parseEvents([{ ...base, start: "nope" }])).toThrow(/Invalid/);
  });
});
