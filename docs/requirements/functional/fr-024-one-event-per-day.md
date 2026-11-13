# FR-024: One event per day

- **Priority:** Must
- **Status:** Accepted

A day has at most one event: either a shift (Miguel works at most one shift per day) or a non-working day ([FR-009](fr-009-non-working-day-events.md)). The day of an event is the day it starts, so a shift that ends after midnight ([FR-017](fr-017-shifts-crossing-midnight.md)) belongs only to the day it starts. A day may have no event, for example if no schedule has been received for it yet. An existing event is never removed, only modified.

## Acceptance criteria

- Given any day with an event, When the calendar is generated or updated, Then that day has exactly one event, never two.
- Given a day that already has an event, When Miguel changes it (photo or command), Then the event is modified, not removed and not duplicated.
