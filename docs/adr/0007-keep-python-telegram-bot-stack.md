# ADR 0007: Keep Python and python-telegram-bot for the bot

- **Status:** Accepted
- **Date:** 2026-11-13

## Context

A basic Telegram bot already runs on the Raspberry Pi ([CON-001](../requirements/constraints/con-001-run-on-pi3.md)): Python 3.12 in a virtual environment, `python-telegram-bot` 22.8 with long polling, and a systemd service. It only has the `/start` and `/health` commands, restricted to a Telegram user ID, and uses about 40 MB of RAM. The owner reports that this stack works very well.

The calendar generator already in the repository is written in TypeScript and runs in GitHub Actions ([ADR 0002](0002-publish-calendar-with-github-pages.md)).

## Decision

The bot is written in **Python** with **`python-telegram-bot`** using long polling. The bot only writes `data/events.json` ([ADR 0003](0003-store-events-in-json-file.md)), and the TypeScript generator in GitHub Actions keeps producing the `.ics` file.

## Alternatives considered

- **Rewrite the bot in TypeScript:** a single language in the repository, but it discards a working stack for no functional gain.

## Consequences

- The repository has two languages. The boundary between them is the format of `data/events.json`, which both sides must respect.
- The bot is light enough for the 1 GB of RAM of the Raspberry Pi.
- Long polling needs no inbound connection to the Raspberry Pi.
