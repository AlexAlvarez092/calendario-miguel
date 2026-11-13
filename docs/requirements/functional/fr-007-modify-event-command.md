# FR-007: Modify event command

- **Priority:** Must
- **Status:** Proposed

The bot provides a command to modify the event of a day (for example, when a colleague asks Miguel to swap a shift mid-month). The interaction is:

1. Miguel invokes the command.
2. Miguel indicates the day to modify. The bot tells Miguel the format (`dd/mm/yyyy`) and Miguel sends the date as text.
3. Miguel indicates whether that day is a shift or a non-working day.
4. If it is a shift, Miguel indicates the start time and the end time.

The event of that day is updated according to Miguel's answers.

## Acceptance criteria

- Given a day that has an event, When Miguel invokes the modify command, indicates the day, says it is a shift and gives the start and end time, Then after he confirms ([FR-022](fr-022-confirm-before-publishing.md)) the event of that day is updated to that shift.
- Given a day that has an event, When Miguel invokes the modify command, indicates the day and says it is a non-working day, Then after he confirms the event of that day is updated to a non-working day.
