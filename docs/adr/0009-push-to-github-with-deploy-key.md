# ADR 0009: Push to GitHub with a deploy key

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

The bot publishes changes by pushing `data/events.json` to the repository from the Raspberry Pi ([ADR 0002](0002-publish-calendar-with-github-pages.md)). The repository may also receive commits from other places, such as the developer's machine.

## Decision

- The bot authenticates with an **SSH deploy key with write access, scoped to this repository only**, stored on the Raspberry Pi.
- Before each push the bot runs `git pull --rebase`. If the pull or the push fails, the bot notifies Miguel and does not retry.

## Alternatives considered

- **Fine-grained personal access token (`contents: write`):** also limited to one repository, but it expires and is tied to a personal account.

## Consequences

- If the key leaks, the damage is limited to this repository.
- Miguel is told when a change could not be published. The message to Miguel is in Spanish ([NFR-006](../requirements/non-functional/nfr-006-bot-messages-in-spanish.md)).
- A failed rebase needs manual intervention on the Raspberry Pi.
