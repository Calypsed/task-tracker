# Task deadlines

## Goal

Allow tasks to have an optional deadline so users can track when a task is due.

## Behavior

- A task can be created with or without a deadline.
- A task's deadline can be changed.
- A task's deadline can be removed.

## Deadline rules

- A deadline is a timezone-aware date and time representing a specific instant in time.
- Different timezone-aware date and time values representing the same instant are equivalent.
- The original timezone offset does not need to be preserved.
- When a deadline is set, it must be strictly later than the current time.
- If an invalid deadline is supplied, the operation is rejected and no changes are made.
- An existing deadline may be removed or replaced with a new valid deadline even if it is already overdue.

## Examples

These deadlines represent the same instant and are considered equivalent:

- `2030-01-01T18:00:00+03:00`
- `2030-01-01T15:00:00+00:00`

If the current time is `2030-01-01T15:00:00+00:00`:

- `2030-01-01T15:00:01+00:00` is a valid new deadline.
- `2030-01-01T15:00:00+00:00` is invalid.
- `2030-01-01T14:59:59+00:00` is invalid.

## Vertical Slices

### Create a task with a deadline
- A task can be created with a specified deadline.
- Attempting to create a task with an invalid deadline does not create a task.

## API contract

- The deadline field in HTTP requests and responses is named `dueAt`.