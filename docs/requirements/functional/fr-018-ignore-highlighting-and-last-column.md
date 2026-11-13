# FR-018: Ignore cell highlighting and the last column

- **Priority:** Must
- **Status:** Accepted

The yellow highlighting of cells and the last column of the table are irrelevant and must be ignored by the bot.

## Acceptance criteria

- Given a photo with yellow-highlighted cells and a last column with extra data, When the bot processes it, Then the highlighting and the last column do not influence the events that are generated.
