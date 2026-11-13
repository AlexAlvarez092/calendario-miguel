# ADR 0003: Store events in `data/events.json`

- **Status:** Accepted
- **Date:** 2026-11-13

## Context

The bot needs a single source of truth for events from which the `.ics` file is generated. Events are already published through the repository ([ADR 0002](0002-publish-calendar-with-github-pages.md)).

## Decision

Events are stored in `data/events.json`, versioned in the repository.

## Alternatives considered

- **SQLite or a JSON file only on the Raspberry Pi:** the data would not be versioned and would be lost if the Pi's storage fails, and the generator in GitHub Actions could not read it.

## Consequences

- Every change is tracked in the Git history.
- The file is public, like the calendar.
- It is already the format used by the existing code.
