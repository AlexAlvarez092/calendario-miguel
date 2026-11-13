# FR-004: Clarify unclear shifts

- **Priority:** Must
- **Status:** Proposed

If the bot cannot understand a shift, it asks Miguel to clarify it before generating any events.

## Acceptance criteria

- Given a photo with a cell of Miguel's row that the bot cannot understand, When the bot processes it, Then it asks Miguel to clarify that cell and does not generate any event until he answers.
