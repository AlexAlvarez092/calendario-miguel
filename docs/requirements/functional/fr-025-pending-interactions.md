# FR-025: Pending interactions

- **Priority:** Must
- **Status:** Proposed

An interaction in progress (a photo being processed, a clarification, a command waiting for an answer, or a summary waiting for confirmation) is kept only in memory and does not expire. Only one interaction can be in progress at a time: when Miguel starts a new one by sending a photo or a command, the one in progress is cancelled, and any late result of the cancelled interaction is discarded. A response from Miguel (for example pressing a confirmation button) belongs to the interaction it was shown for; a response to a cancelled interaction is ignored and can never confirm or answer the new one. Miguel can also cancel it at any time with the `/cancel` command or the Cancel button of the bot's messages. If the bot receives an answer that is not valid for the step in progress, it asks again. If the bot restarts, the interaction is lost and Miguel starts again; nothing is applied without his confirmation ([FR-022](fr-022-confirm-before-publishing.md)).

## Acceptance criteria

- Given an interaction in progress, When Miguel sends `/cancel` or presses the Cancel button, Then the interaction is cancelled and no event is created or updated.
- Given an interaction in progress (a photo being processed, a clarification or a summary waiting for confirmation), When Miguel sends a new photo or starts a new command, Then the interaction in progress is cancelled, none of its changes is applied, and the new interaction starts.
- Given a photo that was being processed when it was cancelled by a new interaction, When its processing finishes afterwards, Then its result is discarded and Miguel is not asked about it.
- Given a summary that was cancelled by a new interaction, When Miguel presses the confirmation button of the old summary while a new summary is pending, Then nothing is applied and the new summary stays pending.
- Given a step that expects a specific answer (for example the type of a non-working day), When Miguel sends text that is not valid for the step, Then the bot asks him to use the buttons of the previous message without cancelling the interaction.
- Given an interaction in progress, When the bot restarts, Then the interaction is lost and no event is created or updated.
