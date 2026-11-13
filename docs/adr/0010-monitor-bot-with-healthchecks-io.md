# ADR 0010: Monitor the bot with healthchecks.io

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

[NFR-007](../requirements/non-functional/nfr-007-downtime-notification.md) requires the developer to be notified when the bot is down. The monitor must run outside the Raspberry Pi, because it cannot notify anything if the Pi itself is off or offline, and it must be free ([CON-002](../requirements/constraints/con-002-everything-free.md)).

## Decision

The bot sends a ping every 5 minutes to a **healthchecks.io** check, configured to send an email to the developer when no ping arrives for 15 minutes.

## Consequences

- The bot depends on one more external service. Its free tier and limits must be reviewed periodically.
- The check URL is a secret and is kept in the `.env` file ([ADR 0005](0005-keep-secrets-in-env-file.md)).
