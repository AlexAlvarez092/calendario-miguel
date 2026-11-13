# FR-009: Non-working day events

- **Priority:** Must
- **Status:** Proposed

Non-working days (rest days, holidays, vacation, compensatory days, requested days (`PEDIDO`), etc.) also generate their own calendar event. The title of the event is the type of non-working day (for example, rest or vacation).

## Acceptance criteria

- Given a day that is a rest day, holiday, vacation or compensatory day, When the events are generated, Then that day has its own event identifying it as a non-working day.
- Given a non-working day of a given type (for example, vacation), When its event is generated, Then the title of the event is that type.
