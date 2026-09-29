### Create task with deadline — remaining work

#### Validation tests

- [x] API rejects a naive `dueAt`.
- [x] Service rejects a naive `due_at` and no task is created.
- [x] Service rejects `due_at <= current time` and no task is created.

#### API

- [x] Creating a task through the API is tested with a deadline.
- [x] Creating a task through the API is tested without a deadline.

#### CLI

- [x] CLI allows creating a task with a deadline.
- [x] CLI still allows creating a task without a deadline.
- [x] Invalid deadlines supplied through CLI result in a failed operation and no task is created.

- [x] CLI can parse add command with due_at
- [x] CLI can use due_at in a handler for add
- [x] CLI can use 3 different formats for datetime
    - [x] Make a parser helper for handler that can parse due at 3 ways
        - [x] ISO format with TZ
        - [x] ISO format date only no time no tz YYYY.MM.DD
        - [x] ISO format date and time no tz YYYY.MM.DDTHH:MM
        - [x] DD.MM.YYYY HH:MM
        - [x] DD.MM.YYYY
        - [x] No datetime
        - [x] parser raises when format is not supported
        - [x] add task handles exception with user output
- [x] Handler correctly handeles service Exception when due at is in the past
- [x] Service correctly processes and raises Exception when due_at is in the past

#### Persistence

- [x] At least one repository contract test uses a non-UTC offset and verifies preservation of the same instant in time. (add task uses fixed offset timezone)

#### Implementation

- [x] Enforce timezone-aware deadlines at the API boundary.
- [x] Enforce deadline rules in the service.
- [x] Add deadline support to the CLI create command.

Also done side effects
Service is now dependent on now provider for ease of testing 