# FR-019: Resending a photo updates the calendar

- **Priority:** Must
- **Status:** Proposed

If Miguel sends a photo of a month that was already processed, the bot updates the calendar only where needed: it creates the events that are missing and updates the events that changed (for example, when the shift of a day that already had an event is different). Events are never deleted ([FR-024](fr-024-one-event-per-day.md)).

## Acceptance criteria

- Given a month already processed, When Miguel sends a photo of the same month where a day has a different shift, Then after he confirms ([FR-022](fr-022-confirm-before-publishing.md)) the event of that day is updated and not duplicated.
- Given a month already processed, When Miguel sends a photo of the same month where a day has no event yet, Then after he confirms the missing event is created and the rest are left unchanged.
