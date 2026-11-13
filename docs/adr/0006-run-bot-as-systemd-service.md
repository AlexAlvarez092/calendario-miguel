# ADR 0006: Run the bot as a systemd service

- **Status:** Accepted
- **Date:** 2026-11-13

## Context

[NFR-003](../requirements/non-functional/nfr-003-automatic-start-and-recovery.md) requires the bot to start automatically and recover from failures on the Raspberry Pi ([CON-001](../requirements/constraints/con-001-run-on-pi3.md)), which has only 1 GB of RAM.

## Decision

The bot runs as a **systemd service** with `Restart=on-failure`, enabled at boot, loading its secrets from the `.env` file ([ADR 0005](0005-keep-secrets-in-env-file.md)). This is how the existing bot already runs on the Raspberry Pi.

## Consequences

- No extra software is needed on Ubuntu, and there is no container overhead.
- Logs are available through `journalctl`.
