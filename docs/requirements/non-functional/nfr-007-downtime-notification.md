# NFR-007: Downtime notification

- **Category:** Availability
- **Priority:** Must
- **Status:** Accepted

The developer is notified by email when the bot has stopped sending its periodic signal ([ADR 0010](../../adr/0010-monitor-bot-with-healthchecks-io.md)) for 15 minutes, so that downtime that automatic recovery ([NFR-003](nfr-003-automatic-start-and-recovery.md)) does not fix does not go unnoticed.

## Acceptance criteria

- Given the bot is not running or the Raspberry Pi has no connection, When 15 minutes pass without a signal from the bot, Then the developer receives an email.
- Given the bot is running normally, When time passes, Then the developer receives no downtime email.
