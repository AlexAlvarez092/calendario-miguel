# FR-020: Detect the month and year of the photo

- **Priority:** Must
- **Status:** Proposed

The bot reads the month and year of the first day of the photo (the table shows it, for example `nov-26`); the month of the following days is deduced from the day numbers, so a photo can cross from one month into the next and does not need to cover a whole month. If it cannot identify the month or the year, it asks Miguel to choose the month of the first day with buttons.

## Acceptance criteria

- Given a photo that shows the month and year (for example `nov-26`), When the bot processes it, Then it uses that month and year for the first day.
- Given a photo whose days go from the end of a month to the start of the next (for example 29, 30, 1, 2), When the bot processes it, Then the days after the change of month are assigned to the next month.
- Given a photo where the bot cannot identify the month or the year, When it processes it, Then it asks Miguel for the month with buttons before generating any event.
