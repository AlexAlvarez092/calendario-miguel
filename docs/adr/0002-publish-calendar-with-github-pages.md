# ADR 0002: Publish the calendar with GitHub Pages

- **Status:** Accepted
- **Date:** 2026-11-13

## Context

Friends subscribe to the calendar through a URL. The bot runs on the Raspberry Pi ([CON-001](../requirements/constraints/con-001-run-on-pi3.md)) and everything must be free ([CON-002](../requirements/constraints/con-002-everything-free.md)).

## Decision

The bot pushes changes to `data/events.json` ([ADR 0003](0003-store-events-in-json-file.md)) to the repository. A GitHub Actions workflow generates the `.ics` file from it and **GitHub Pages** serves it at a public URL.

## Alternatives considered

- **Serve the `.ics` from the Raspberry Pi (for example through a Cloudflare Tunnel):** free, but it makes the calendar depend on the Pi and its connection being up, and it exposes the Pi to the internet.

## Consequences

- No need to expose the Raspberry Pi to the internet.
- The calendar is publicly readable, as accepted in [NFR-001](../requirements/non-functional/nfr-001-privacy.md).
- The Raspberry Pi needs credentials with write access to the repository.
