# Overview

## Goal

Automate two things for a childhood friend (Miguel) who works in shifts:

1. Generating calendar events from his printed shift schedule.
2. Sharing those events with his friends.

## Current situation

Periodically Miguel receives, via WhatsApp, a photo of a printed calendar with his shifts for the following weeks. It can cover a whole month or only part of it, and it can cross from one month into the next. He manually creates each shift as an event in his calendar app. He also shares the photo with some friends so they know when he is available to make plans.

## Scope

**In scope**

- Every active (not Dropped) requirement in [functional/](functional/).

**Out of scope**

- Restricting access to the calendar (see [NFR-001](non-functional/nfr-001-privacy.md)).
- Bot actions other than those listed in the functional requirements.

## Users

| Role | Description |
|------|-------------|
| Miguel | Works in shifts. Receives the printed schedule and wants his shifts as calendar events. |
| Friends | Receive Miguel's schedule to know when to make plans with him. |

## Glossary

| Term | Definition |
|------|------------|
| Shift | A work period of a day, with a start time and an end time. It may end after midnight. |
| Non-working day | A day without a shift: rest day, holiday, vacation, compensatory day, requested day (`PEDIDO`), etc. |
| Event | The calendar entry of a day, either a shift or a non-working day. |
