# FR-004: Clarify unclear shifts

- **Priority:** Must
- **Status:** Accepted

If the bot cannot understand a shift, it asks Miguel to clarify it before generating any events. For each cell of Miguel's row, the bot obtains from the AI service the literal text of the cell, its interpretation and the annotations it ignored ([FR-016](fr-016-classify-each-day.md)), and checks the interpretation itself instead of trusting the AI service. The bot treats a cell as not understood when any of these is true:

- The AI service flags it as uncertain.
- The literal text contains something that is not explained by the interpretation or by the ignored annotations (for example `debido 02-11` interpreted as a shift from 02:00 to 11:00), even if the AI service does not flag it as uncertain.
- The start and end time of the interpretation do not appear in the literal text in the same order (for example `10-18` interpreted as a shift from 18:00 to 10:00).
- A day is missing between the days of Miguel's row (the photo can start and end on any day, so days before the first or after the last day of the photo are not missing), or the days of the photo are not coherent (for example a day number that goes down in the middle of a month, or a day that does not exist in its month).

## Acceptance criteria

- Given a photo with a cell of Miguel's row that the AI service flags as uncertain, When the bot processes it, Then it asks Miguel to clarify that cell and does not generate any event until he answers.
- Given a cell whose literal text contains something that neither the interpretation nor the ignored annotations explain (for example `debido 02-11`), When the bot processes it, Then it asks Miguel to clarify that cell, even if the AI service did not flag it as uncertain, and does not generate any event until he answers.
- Given a cell whose literal text is fully explained by the interpretation and the ignored annotations (for example `10-18 HT`), When the bot processes it, Then it does not ask Miguel about that cell.
- Given a cell with the literal text `10-18` whose interpretation is a shift from 18:00 to 10:00, When the bot processes it, Then it asks Miguel to clarify that cell and does not generate any event until he answers.
- Given a photo where a day is missing between the first and the last day of Miguel's row, When the bot processes it, Then it tells Miguel which days are missing, asks for each one, and does not generate any event until he answers.
- Given a photo that does not start on the first day of a month (for example it starts on the 12th), When the bot processes it, Then it does not ask about the days before the first one.
- Given a photo whose days are not coherent (for example a day that does not exist in its month), When the bot processes it, Then it tells Miguel that it cannot use the photo and does not generate any event.
