# FR-005: Add event command

- **Priority:** Must
- **Status:** Accepted

The bot provides a command to add the event of a day (for example, a day of a future month whose schedule has not been received, but whose shift Miguel already knows). It is expected to be rarely used. Miguel starts it from the bot's menu or with the `/add` command, and answers with buttons ([FR-026](fr-026-interaction-with-buttons.md)). If the day already has an event, the bot asks Miguel whether he wants to replace it. If the day is not a shift, the bot asks for the type of non-working day, offering buttons (rest, vacation, holiday, compensatory, requested) or free text ([FR-009](fr-009-non-working-day-events.md)).

## Acceptance criteria

- Given a day that does not have an event yet, When Miguel uses the add command and provides the day and whether it is a shift (with start and end time) or a non-working day (with its type), Then an event is created for that day, after Miguel confirms ([FR-022](fr-022-confirm-before-publishing.md)).
- Given a day that already has an event, When Miguel uses the add command and provides that day, Then the bot asks whether he wants to replace the existing event, and only if he accepts does it continue and, after he confirms ([FR-022](fr-022-confirm-before-publishing.md)), replace the event.
- Given a day that already has an event, When Miguel declines to replace it, Then the existing event is left unchanged.
