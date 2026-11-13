# NFR-005: Bot access restricted to Miguel

- **Category:** Security
- **Priority:** Must
- **Status:** Proposed

Only Miguel can use the Telegram bot, and therefore create or modify calendar events.

## Acceptance criteria

- Given a Telegram user who is not Miguel, When he sends a photo or a command to the bot, Then the bot does not process it and no event is created or modified.
- Given Miguel, When he sends a photo or a command to the bot, Then the bot processes it.
