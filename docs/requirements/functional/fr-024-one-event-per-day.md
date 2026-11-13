# FR-024: One event per day

- **Priority:** Must
- **Status:** Proposed

Every day of the calendar has exactly one event: either a shift (Miguel works at most one shift per day) or a non-working day ([FR-009](fr-009-non-working-day-events.md)). An existing event is therefore never removed, only modified.

## Acceptance criteria

- Given any day with an event, When the calendar is generated or updated, Then that day has exactly one event, never two.
- Given a day that already has an event, When Miguel changes it (photo or command), Then the event is modified, not removed and not duplicated.
