# ADR 0009: Push to GitHub with a deploy key

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

The bot publishes changes by pushing `data/events.json` to the repository from the Raspberry Pi ([ADR 0002](0002-publish-calendar-with-github-pages.md)). The repository may also receive commits from other places, such as the developer's machine, and the Raspberry Pi may have no connection when Miguel confirms a change.

## Decision

- The bot authenticates with an **SSH deploy key with write access, scoped to this repository only**, stored on the Raspberry Pi.
- A change confirmed by Miguel is saved as a local commit. Before each push the bot runs `git pull --rebase`.
- If the pull or the push fails, the commit stays pending and the bot retries every minute. It also retries when the next change is confirmed.
- If the rebase fails (a conflict), the bot notifies Miguel, because retrying cannot fix it.
- The bot does not check the result of the GitHub Actions workflow or of the Pages deployment. GitHub already emails the developer when a workflow fails.

## Alternatives considered

- **Fine-grained personal access token (`contents: write`):** also limited to one repository, but it expires and is tied to a personal account.
- **Discard the change and ask Miguel to repeat it:** simpler, but Miguel would lose work because of a network failure.

## Consequences

- If the key leaks, the damage is limited to this repository.
- A change can stay unpublished while there is no connection, and it is published once the connection returns.
- The notification to Miguel is in Spanish ([NFR-006](../requirements/non-functional/nfr-006-user-facing-text-in-spanish.md)).
- A failed rebase needs manual intervention on the Raspberry Pi.
