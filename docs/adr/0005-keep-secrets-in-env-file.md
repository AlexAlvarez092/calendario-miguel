# ADR 0005: Keep secrets in an `.env` file loaded by systemd

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

The bot needs secrets: the Telegram bot token, the Gemini API key, the GitHub credentials ([ADR 0002](0002-publish-calendar-with-github-pages.md)) and the Telegram user ID of Miguel ([ADR 0004](0004-restrict-access-by-telegram-user-id.md)). The repository is public, so they must never be committed.

## Decision

Secrets live in an `.env` file on the Raspberry Pi, outside the repository, readable only by the bot user (permissions `600`) and loaded by the systemd service through `EnvironmentFile`.

## Consequences

- No secret is ever in the repository.
- Secrets are stored in plain text on the Raspberry Pi, protected only by file permissions.
- Rotating a secret requires editing the file and restarting the service.
