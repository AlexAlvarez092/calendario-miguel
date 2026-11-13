# FR-022: Confirm before publishing

- **Priority:** Must
- **Status:** Proposed

Before creating or updating events, whether from a photo or from a command ([FR-005](fr-005-add-event-command.md), [FR-007](fr-007-modify-event-command.md)), the bot always shows Miguel a summary of the changes and applies them only after he confirms. Only one summary can be pending at a time: starting a new flow cancels the pending one.

## Acceptance criteria

- Given changes to apply from a photo or from a command, When the bot has them ready, Then it shows Miguel a summary of the changes and applies none of them until he confirms.
- Given a summary shown to Miguel, When he rejects it, Then no event is created or updated.
- Given a summary pending confirmation, When Miguel sends a new photo or starts a new command, Then the pending summary is cancelled, none of its changes is applied, and the new flow starts.
