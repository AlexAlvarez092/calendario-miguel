# Overview

## Goal

Automate two things for a childhood friend (Miguel) who works in shifts:

1. Generating calendar events from his monthly shift schedule.
2. Sharing those events with his friends.

## Current situation

Every month Miguel receives, via WhatsApp, a photo of a printed calendar with his shifts for the following month. He manually creates each shift as an event in his calendar app. He also shares the photo with some friends so they know when he is available to make plans.

## Scope

**In scope**

- Everything described in [functional/](functional/).

**Out of scope**

- Restricting access to the calendar (see [NFR-001](non-functional/nfr-001-privacy.md)).
- Bot actions other than those listed in the functional requirements.

## Users

| Role | Description |
|------|-------------|
| Miguel | Works in shifts. Receives the monthly printed schedule and wants his shifts as calendar events. |
| Friends | Receive Miguel's schedule to know when to make plans with him. |

## Glossary

| Term | Definition |
|------|------------|
| Shift | A work period of a day, with a start time and an end time. It may end after midnight. |
| Non-working day | A day without a shift: rest day, holiday, vacation, compensatory day, etc. |
| Event | The calendar entry of a day, either a shift or a non-working day. |
