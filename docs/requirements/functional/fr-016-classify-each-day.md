# FR-016: Classify each day as shift or non-working day

- **Priority:** Must
- **Status:** Proposed

For each day, the bot must clearly identify whether Miguel is working (and the start and end time of the shift) or not working. Annotations next to or instead of the schedule (for example `PEDIDO`, `HT`, `debido`) are taken into account only if they are relevant to that distinction; otherwise the AI service reports them as ignored and they are ignored.

## Acceptance criteria

- Given a cell with a start and end time, When the bot processes it, Then the day is a shift with that start and end time.
- Given a cell with an annotation that does not change whether Miguel works or the shift times (for example `PEDIDO`), When the bot processes it, Then the annotation is ignored and the day is classified by its schedule.
