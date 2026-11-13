# FR-004: Clarify unclear shifts

- **Priority:** Must
- **Status:** Proposed

If the bot cannot understand a shift, it asks Miguel to clarify it before generating any events. The bot treats a cell as not understood when any of these is true:

- The AI service flags it as uncertain.
- It is neither a start and end time nor a known non-working day marker (for example `DESCANSO` or `VACACIONES`), regardless of the AI service flagging it.
- A day of the month is missing from Miguel's row, or there are days that do not belong to the month.

## Acceptance criteria

- Given a photo with a cell of Miguel's row that the AI service flags as uncertain, When the bot processes it, Then it asks Miguel to clarify that cell and does not generate any event until he answers.
- Given a photo with a cell of Miguel's row that is neither a start and end time nor a known non-working day marker (for example `debido 02-11`), When the bot processes it, Then it asks Miguel to clarify that cell, even if the AI service did not flag it as uncertain, and does not generate any event until he answers.
- Given a photo where a day of the month is missing from Miguel's row or a day does not belong to the month, When the bot processes it, Then it tells Miguel which days are affected and does not generate any event until he answers.
