# NFR-005: Bot access restricted to authorized users

- **Category:** Security
- **Priority:** Must
- **Status:** Accepted

Only the authorized users can use the Telegram bot, and therefore create or modify calendar events. The authorized users are Miguel and the developer. Each of them has his own interaction in progress ([FR-025](../functional/fr-025-pending-interactions.md)).

## Acceptance criteria

- Given a Telegram user who is not authorized, When he sends a photo, a command or presses a button of the bot, Then the bot does not process it and no event is created or modified.
- Given an authorized user, When he sends a photo or a command to the bot, Then the bot processes it.
