# FR-009: Non-working day events

- **Priority:** Must
- **Status:** Proposed

Non-working days (rest days, holidays, vacation, compensatory days, etc.) also generate their own calendar event, so that a day without a shift is never ambiguous (no shift versus an event that was not generated).

## Acceptance criteria

- Given a day that is a rest day, holiday, vacation or compensatory day, When the events are generated, Then that day has its own event identifying it as a non-working day, so it is never ambiguous with a day whose event was not generated.
