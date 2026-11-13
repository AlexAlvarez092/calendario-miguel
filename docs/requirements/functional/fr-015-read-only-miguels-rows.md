# FR-015: Read only Miguel's rows

- **Priority:** Must
- **Status:** Accepted

The photo is a table with the schedule of several people. The bot always looks for the row(s) labeled "Miguel" (one per week block) and uses only those; the rows of other people are ignored.

## Acceptance criteria

- Given a photo of a table with the schedule of several people, When the bot processes it, Then it uses only the row(s) labeled "Miguel" and generates no event from the rows of other people.
