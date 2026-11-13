# ADR 0004: Restrict access by Telegram user ID

- **Status:** Accepted
- **Date:** 2026-11-13

## Context

[NFR-005](../requirements/non-functional/nfr-005-bot-access-restricted-to-authorized-users.md) requires that only the authorized users (Miguel and the developer) can use the bot.

## Decision

The bot only accepts messages from the Telegram user IDs in a list configured on the Raspberry Pi (`TELEGRAM_ALLOWED_IDS`, separated by commas). Messages from any other user are ignored. Every authorized user has his own interaction in progress, so one cannot cancel or answer the interaction of the other.

## Consequences

- Telegram user IDs cannot be changed by the user, unlike usernames.
- If an authorized user changes Telegram account, the configured list must be updated.
- Notifications that the bot sends on its own, such as a publication conflict, go to all the authorized users.
