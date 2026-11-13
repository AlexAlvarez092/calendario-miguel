# ADR 0004: Restrict access by Telegram user ID

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

[NFR-005](../requirements/non-functional/nfr-005-bot-access-restricted-to-miguel.md) requires that only Miguel can use the bot.

## Decision

The bot only accepts messages from the Telegram user ID of Miguel, configured on the Raspberry Pi. Messages from any other user are ignored.

## Consequences

- Telegram user IDs cannot be changed by the user, unlike usernames.
- If Miguel changes Telegram account, the configured ID must be updated.
