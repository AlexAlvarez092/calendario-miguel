# ADR 0011: Test photo reading with a synthetic photo

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

The real schedule photo contains the names and shifts of other people, and the repository is public. The bot reads photos with an AI service ([ADR 0001](0001-use-ai-to-read-schedule-photo.md)), so photo reading needs to be tested.

## Decision

- The repository contains a **synthetic photo** of a schedule, made up with fictional names, to be used in tests.
- The real photo is never committed. It is only used in manual tests.

## Consequences

- No personal data of third parties is published.
- The synthetic photo must resemble the real one (table layout and annotations) for the tests to be meaningful.
