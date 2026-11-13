# FR-007: Modify event command

- **Priority:** Must
- **Status:** Accepted

The bot provides a command to modify the event of a day (for example, when a colleague asks Miguel to swap a shift mid-month). The interaction is:

1. Miguel invokes the command from the bot's menu or with the `/modify` command.
2. Miguel indicates the day to modify by choosing it in a calendar of buttons ([FR-026](fr-026-interaction-with-buttons.md)). If that day has no event, the bot tells him to use the add command instead.
3. Miguel indicates whether that day is a shift or a non-working day.
4. If it is a shift, Miguel chooses the start time and the end time with buttons. Otherwise, the bot asks for the type of non-working day, offering buttons (rest, vacation, holiday, compensatory, requested) or free text ([FR-009](fr-009-non-working-day-events.md)).

The event of that day is updated according to Miguel's answers.

## Acceptance criteria

- Given a day that has an event, When Miguel invokes the modify command, indicates the day, says it is a shift and gives the start and end time, Then after he confirms ([FR-022](fr-022-confirm-before-publishing.md)) the event of that day is updated to that shift.
- Given a day that has an event, When Miguel invokes the modify command, indicates the day and says it is a non-working day of a given type, Then after he confirms the event of that day is updated to a non-working day with that type as title.
