# ADR 0008: Event format in `data/events.json`

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

Events are stored in `data/events.json` ([ADR 0003](0003-store-events-in-json-file.md)). The bot writes the file and the TypeScript generator reads it ([ADR 0007](0007-keep-python-telegram-bot-stack.md)), so the format is the contract between them. Every day has exactly one event ([FR-024](../requirements/functional/fr-024-one-event-per-day.md)), and non-working days are all-day events titled with their type ([FR-009](../requirements/functional/fr-009-non-working-day-events.md), [FR-010](../requirements/functional/fr-010-non-working-days-all-day.md)). Resending a month must update the events without duplicating them.

## Decision

- The event `id` is the date of the day (`YYYY-MM-DD`), for shifts and non-working days alike. It is also the identifier of the event in the `.ics` file.
- A shift has `start` and `end` as `YYYY-MM-DDTHH:mm` (Europe/Madrid). A shift that ends after midnight has an `end` on the following day.
- A non-working day has `start` as `YYYY-MM-DD` and no `end`, which the generator already renders as an all-day event.
- `title` is the type of non-working day for non-working days.

## Consequences

- Creating an event for a day that already has one replaces it, so duplicates are impossible by construction.
- The existing generator comment on `EventInput.id` says the id must never be derived from the date or time. With this decision it is derived from the date, so that comment has to be changed when the bot is implemented. The rest of the generator already supports this format.
- The existing `data/events.json` uses `turno-YYYY-MM-DD` ids and must be migrated.
