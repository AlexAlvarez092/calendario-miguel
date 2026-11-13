# FR-021: Time zone

- **Priority:** Must
- **Status:** Proposed

All shift times are in the `Europe/Madrid` time zone.

## Acceptance criteria

- Given a shift on a day when the clocks change in Europe/Madrid, When its event is created, Then its start and end times are the local times shown in the photo.
