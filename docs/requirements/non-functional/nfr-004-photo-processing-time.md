# NFR-004: Photo processing time

- **Category:** Performance
- **Priority:** Must
- **Status:** Proposed

The bot responds to Miguel after he sends a photo in at most 6 minutes.

## Acceptance criteria

- Given Miguel sends a photo of the schedule, When the bot processes it, Then Miguel receives a response (the summary to confirm, a clarification question or an error message) within 6 minutes.
