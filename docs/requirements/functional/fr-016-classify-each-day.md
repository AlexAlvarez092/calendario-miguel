# FR-016: Classify each day as shift or non-working day

- **Priority:** Must
- **Status:** Accepted

For each day, the bot must clearly identify whether Miguel is working (and the start and end time of the shift) or not working. Annotations next to or instead of the schedule (for example `HT`, `debido`) are taken into account only if they are relevant to that distinction; otherwise the AI service reports them as ignored and they are ignored. The exception is `PEDIDO` next to a schedule: it takes precedence and the day is a non-working day of type Pedido, because the original shift was requested off.

## Acceptance criteria

- Given a cell with a start and end time, When the bot processes it, Then the day is a shift with that start and end time.
- Given a cell with an annotation that does not change whether Miguel works or the shift times (for example `HT`), When the bot processes it, Then the annotation is ignored and the day is classified by its schedule.
- Given a cell with a schedule and `PEDIDO` (for example `10-18 PEDIDO`), When the bot processes it, Then the day is a non-working day of type Pedido, not a shift.
