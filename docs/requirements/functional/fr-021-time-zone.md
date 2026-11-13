# FR-021: Time zone

- **Priority:** Must
- **Status:** Proposed

All shift times are in the `Europe/Madrid` time zone. Local times that do not exist or happen twice on a clock change night are not handled specially: the time zone library resolves them.

## Acceptance criteria

- Given a shift on a day when the clocks change in Europe/Madrid, When its event is created, Then its start and end times are the local times shown in the photo, except those that do not exist or happen twice on that night, which are resolved by the time zone library (for example a nonexistent `02:30` becomes `03:30`).
