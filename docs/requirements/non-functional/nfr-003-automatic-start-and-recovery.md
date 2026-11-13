# NFR-003: Automatic start and recovery

- **Category:** Availability
- **Priority:** Must
- **Status:** Proposed

The bot starts automatically when the Raspberry Pi starts and restarts automatically if it stops unexpectedly.

## Acceptance criteria

- Given the Raspberry Pi is powered on or rebooted, When the system finishes starting, Then the bot is running and answers Miguel without anyone starting it manually.
- Given the bot process stops unexpectedly, When it stops, Then it is restarted automatically and answers Miguel again.
