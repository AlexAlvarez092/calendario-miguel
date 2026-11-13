# FR-011: Subscription URL

- **Priority:** Must
- **Status:** Accepted

The calendar is published at a URL that anyone with the link can subscribe to from a calendar app.

## Acceptance criteria

- Given the calendar URL, When anyone adds it as a subscription in a calendar app, Then the app shows the events of the calendar.
- Given the calendar URL, When someone adds the subscription without any login or account, Then it works.
- Given a friend and Miguel, When each of them adds the same URL as a subscription, Then both see the same events of the calendar.
