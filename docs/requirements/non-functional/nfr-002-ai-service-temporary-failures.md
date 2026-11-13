# NFR-002: Temporary failures of the AI service

- **Category:** Reliability
- **Priority:** Must
- **Status:** Proposed

When the AI service fails temporarily (for example with HTTP 503 "high demand" errors), the bot retries automatically a few times. Each attempt times out after 60 seconds, and a timeout counts as a temporary failure. The bot gives up when the retries run out or when 4 minutes have passed since the photo arrived, whichever comes first, and then informs Miguel through Telegram.

## Acceptance criteria

- Given the AI service returns a temporary error (for example HTTP 503) or does not answer within 60 seconds, When the bot processes a photo, Then it retries up to 3 times, waiting 10, 30 and 60 seconds before each retry.
- Given all the retries fail or 4 minutes have passed since the photo arrived, When the bot gives up, Then it informs Miguel through Telegram that the photo could not be processed, within the time limit of [NFR-004](nfr-004-photo-processing-time.md).
