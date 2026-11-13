# FR-004: Clarify unclear shifts

- **Priority:** Must
- **Status:** Proposed

If the bot cannot understand a shift, it asks Miguel to clarify it before generating any events. For each cell of Miguel's row, the bot obtains from the AI service the literal text of the cell, its interpretation and the annotations it ignored ([FR-016](fr-016-classify-each-day.md)), and checks the interpretation itself instead of trusting the AI service. The bot treats a cell as not understood when any of these is true:

- The AI service flags it as uncertain.
- The literal text contains something that is not explained by the interpretation or by the ignored annotations (for example `debido 02-11` interpreted as a shift from 02:00 to 11:00), even if the AI service does not flag it as uncertain.
- A day of the month is missing from Miguel's row, or there are days that do not belong to the month.

## Acceptance criteria

- Given a photo with a cell of Miguel's row that the AI service flags as uncertain, When the bot processes it, Then it asks Miguel to clarify that cell and does not generate any event until he answers.
- Given a cell whose literal text contains something that neither the interpretation nor the ignored annotations explain (for example `debido 02-11`), When the bot processes it, Then it asks Miguel to clarify that cell, even if the AI service did not flag it as uncertain, and does not generate any event until he answers.
- Given a cell whose literal text is fully explained by the interpretation and the ignored annotations (for example `10-18 PEDIDO`), When the bot processes it, Then it does not ask Miguel about that cell.
- Given a photo where a day of the month is missing from Miguel's row or a day does not belong to the month, When the bot processes it, Then it tells Miguel which days are affected and does not generate any event until he answers.
