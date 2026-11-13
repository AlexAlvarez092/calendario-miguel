# FR-017: Shifts that cross midnight

- **Priority:** Must
- **Status:** Accepted

A shift that ends after midnight (for example `18-02`, or `16-00` ending at 00:00) is a single event that starts on the day of the shift and ends on the following day.

## Acceptance criteria

- Given a shift `18-02` on a given day, When its event is created, Then it is a single event that starts at 18:00 on that day and ends at 02:00 on the following day.
- Given a shift `16-00` on a given day, When its event is created, Then it is a single event that starts at 16:00 on that day and ends at 00:00 on the following day.
