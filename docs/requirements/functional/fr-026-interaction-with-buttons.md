# FR-026: Interaction with buttons

- **Priority:** Must
- **Status:** Proposed

Miguel answers the bot with buttons wherever possible, instead of typing commands or values. The bot offers a menu (shown with `/start`) with the add and modify options ([FR-005](fr-005-add-event-command.md), [FR-007](fr-007-modify-event-command.md)); the commands remain as shortcuts. The bot asks for:

- A day with a calendar of buttons for a month, with arrows to change the month.
- A time with buttons for the hour (00 to 23). Minutes are not asked: shifts always start and end on the hour (`HH:00`).
- The kind of day (shift or non-working day), the type of non-working day, confirmations and the month of a photo with buttons.

Every message with buttons includes a Cancel button ([FR-025](fr-025-pending-interactions.md)). The only free text accepted is the type of a non-working day other than the offered ones ([FR-009](fr-009-non-working-day-events.md)).

## Acceptance criteria

- Given Miguel sends `/start`, When the bot answers, Then it shows buttons to add and to modify an event.
- Given Miguel starts the add or modify option, When the bot asks for the day, Then it shows a calendar of buttons for the current month with arrows to go to the previous and next months, and Miguel's choice is used without typing a date.
- Given the bot asks for a shift time, When Miguel chooses the hour, Then that time with minutes `00` is used.
- Given a shift whose end time is the same as its start time, When Miguel chooses it, Then the bot asks for the end time again.
- Given a message with buttons, When Miguel presses its Cancel button, Then the interaction is cancelled.
