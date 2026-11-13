# FR-005: Add event command

- **Priority:** Must
- **Status:** Proposed

The bot provides a command to add the event of a day that does not have one yet (for example, a day of a future month whose schedule has not been received, but whose shift Miguel already knows). It is expected to be rarely used.

## Acceptance criteria

- Given a day that does not have an event yet, When Miguel uses the add command and provides the day and whether it is a shift (with start and end time) or a non-working day, Then an event is created for that day, after Miguel confirms ([FR-022](fr-022-confirm-before-publishing.md)).
