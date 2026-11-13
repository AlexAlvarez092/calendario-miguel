# FR-003: Generate events from the photo

- **Priority:** Must
- **Status:** Accepted

From the photo, the bot extracts the shifts and generates the calendar events without further manual steps, apart from the clarifications of [FR-004](fr-004-clarify-unclear-shifts.md) and the confirmation of [FR-022](fr-022-confirm-before-publishing.md).

## Acceptance criteria

- Given a photo of the schedule where the bot understands all of Miguel's cells (none needs clarification according to [FR-004](fr-004-clarify-unclear-shifts.md)), When the bot processes it, Then it generates the events of all the days of the month without any manual step by Miguel other than confirming ([FR-022](fr-022-confirm-before-publishing.md)).
