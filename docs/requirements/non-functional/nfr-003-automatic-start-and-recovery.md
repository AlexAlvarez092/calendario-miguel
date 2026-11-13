# NFR-003: Automatic start and recovery

- **Category:** Availability
- **Priority:** Must
- **Status:** Accepted

The bot starts automatically when the Raspberry Pi starts and restarts automatically if it stops unexpectedly because of an error. The bot is not expected to exit without an error on its own, so stopping it deliberately (for example with `systemctl stop`) does not restart it.

## Acceptance criteria

- Given the Raspberry Pi is powered on or rebooted, When the system finishes starting, Then the bot is running and answers Miguel without anyone starting it manually.
- Given the bot process stops because of an error (it is killed with `SIGKILL` or crashes with an unhandled exception), When it stops, Then it is restarted automatically and answers Miguel again.
