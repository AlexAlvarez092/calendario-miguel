# ADR 0002: Publish the calendar with GitHub Pages

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

Friends subscribe to the calendar through a URL. The bot runs on the Raspberry Pi ([CON-001](../requirements/constraints/con-001-run-on-pi3.md)) and everything must be free ([CON-002](../requirements/constraints/con-002-everything-free.md)).

## Decision

The bot commits and pushes the generated `.ics` file to the repository, and **GitHub Pages** serves it at a public URL.

## Consequences

- No need to expose the Raspberry Pi to the internet.
- Anyone with the URL can read the calendar. This is accepted for now.
- The Raspberry Pi needs credentials with write access to the repository.
