# NFR-002: Temporary failures of the AI service

- **Category:** Reliability
- **Priority:** Must
- **Status:** Proposed

When the AI service fails temporarily (for example with HTTP 503 "high demand" errors), the bot retries automatically a few times. If the failure persists, it informs Miguel through Telegram.

## Acceptance criteria

- Given the AI service returns a temporary error (for example HTTP 503), When the bot processes a photo, Then it retries up to 3 times, waiting 10, 30 and 60 seconds before each retry.
- Given all the retries fail, When the bot gives up, Then it informs Miguel through Telegram that the photo could not be processed, within the time limit of [NFR-004](nfr-004-photo-processing-time.md).
