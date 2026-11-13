# FR-020: Detect the month and year of the photo

- **Priority:** Must
- **Status:** Proposed

The bot reads the month and year from the photo (the table shows it, for example `nov-26`). If it cannot identify them, it asks Miguel.

## Acceptance criteria

- Given a photo that shows the month and year (for example `nov-26`), When the bot processes it, Then it uses that month and year for the events.
- Given a photo where the bot cannot identify the month or the year, When it processes it, Then it asks Miguel for them before generating any event.
