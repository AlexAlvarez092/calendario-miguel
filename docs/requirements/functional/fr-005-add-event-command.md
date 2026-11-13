# FR-005: Add event command

- **Priority:** Must
- **Status:** Proposed

The bot provides a command to add the event of a day (for example, a day of a future month whose schedule has not been received, but whose shift Miguel already knows). It is expected to be rarely used. If the day already has an event, the bot asks Miguel whether he wants to replace it.

## Acceptance criteria

- Given a day that does not have an event yet, When Miguel uses the add command and provides the day and whether it is a shift (with start and end time) or a non-working day, Then an event is created for that day, after Miguel confirms ([FR-022](fr-022-confirm-before-publishing.md)).
- Given a day that already has an event, When Miguel uses the add command and provides that day, Then the bot asks whether he wants to replace the existing event, and only if he accepts does it continue and, after he confirms ([FR-022](fr-022-confirm-before-publishing.md)), replace the event.
- Given a day that already has an event, When Miguel declines to replace it, Then the existing event is left unchanged.
