# FR-025: Pending interactions

- **Priority:** Must
- **Status:** Proposed

An interaction in progress (a clarification, a command waiting for an answer, or a summary waiting for confirmation) is kept only in memory and does not expire. Miguel can cancel it at any time with the `/cancel` command. If the bot receives an answer that is not valid for the step in progress, it asks again. If the bot restarts, the interaction is lost and Miguel starts again; nothing is applied without his confirmation ([FR-022](fr-022-confirm-before-publishing.md)).

## Acceptance criteria

- Given an interaction in progress, When Miguel sends `/cancel`, Then the interaction is cancelled and no event is created or updated.
- Given a step that expects a specific answer (for example a date in `dd/mm/yyyy` format), When Miguel sends an answer that is not valid, Then the bot explains what it expects and asks again without cancelling the interaction.
- Given an interaction in progress, When the bot restarts, Then the interaction is lost and no event is created or updated.
