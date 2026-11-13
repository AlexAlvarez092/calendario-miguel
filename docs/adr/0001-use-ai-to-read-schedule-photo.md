# ADR 0001: Use AI to read the schedule photo

- **Status:** Proposed
- **Date:** 2026-11-13

## Context

[FR-003](../requirements/functional/fr-003-generate-events-from-photo.md) requires the bot to extract the shifts from a photo of a printed monthly calendar, and [FR-004](../requirements/functional/fr-004-clarify-unclear-shifts.md) requires it to detect what it cannot understand. [CON-002](../requirements/constraints/con-002-everything-free.md) requires everything to be free, and [CON-001](../requirements/constraints/con-001-run-on-pi3.md) requires the bot to run on a Raspberry Pi 3 with 1 GB of RAM. Usage is tiny: about one photo per month.

## Decision

Use an AI service with vision support to read the photo, specifically the **Google Gemini API free tier with the `gemini-3.5-flash-lite` model**.

## Alternatives considered

- **Local OCR (for example Tesseract):** free and offline, but it returns text, not a grid, so detecting the calendar structure would be a significant engineering effort, and the Raspberry Pi is limited.
- **Manual entry only:** discarded because [FR-003](../requirements/functional/fr-003-generate-events-from-photo.md) requires no further manual steps.
- **Groq (`qwen/qwen3.8-27b`):** free, but with a real photo it read 19 of 28 days correctly, mixing up rows of other people. Discarded.
- **Other free services** (Cloudflare Workers AI, OpenRouter `:free` models): not tested. Not usable under [CON-002](../requirements/constraints/con-002-everything-free.md): Mistral API, Hugging Face, Google Cloud Vision. GitHub Models has been retired.

## Test results

Tested on 2026-11-13 with a real photo of the schedule, asking for the 28 days of Miguel's rows and comparing with a manual reading:

- `gemini-3.5-flash-lite`: 28/28, 27/28 and 27/28 in three runs. The only mistake was a `debido 02-11` cell, which was read as a shift from 02:00 to 11:00 without flagging any uncertainty.
- `qwen/qwen3.8-27b` (Groq): 19/28.
- `gemini-3.8-flash` and `gemma-4-31b-it`: no result (connection errors and timeouts).

## Consequences

- The bot depends on an external AI service. Gemini returned temporary 503 "high demand" errors during the test, so requests must be retried.
- Cells that are not a plain schedule (such as `debido ...`) can be misread without being flagged. The bot must not rely only on the model's own uncertainty flag to satisfy [FR-004](../requirements/functional/fr-004-clarify-unclear-shifts.md).
- **Accepted risk:** the Gemini API terms (https://ai.google.dev/gemini-api/terms, effective 2026-03-23) state that apps serving users in the EEA, Switzerland or the UK may only use the paid services. Using the free tier from Spain may violate these terms. The project accepts this risk for now.
- Free-tier limits and model names change often. The model and the limits must be reviewed periodically.
