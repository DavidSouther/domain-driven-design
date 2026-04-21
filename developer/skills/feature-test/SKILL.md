---
name: feature-test
description: Use when a design doc has been reviewed and cleared — writes a single executable test encoding a user story before any implementation begins
---

# developer:feature-test

## Overview

Writes a single executable feature test that encodes a user story end-to-end. This is the middle-loop entry point. It defines what "done" looks like before any implementation begins.

**Announce at start:** "Using developer:feature-test to write the feature test for [summary of feature]."

**Trigger:** Design doc draft marker has been cleared by a human.

**Hard gate:** Do not write any implementation code outside the feature test itself. Do not scaffold any project structure beyond the test file itself. Decline any request to do so in this session.

## Behavior

1. Read the cleared design doc from the session folder.
2. Write a user story in plain language (Given/When/Then or narrative form).
3. Write one executable feature test that runs end-to-end through the user story.
4. Save both artifacts and mark the feature test file as a draft.
5. Add a TASK to perform a final refactoring and review once the entire feature is completed.
6. Stop. Decline to implement any code that makes the test pass.

## User Story Format

Write the user story in plain language before the executable test. Use Given/When/Then for discrete interactions, or a short narrative for flows:

```markdown
## User Story

**Given** a user with an active account
**When** they submit the login form with valid credentials
**Then** they are redirected to their dashboard and see a welcome message
```

or narrative:

```markdown
## User Story

A returning user opens the app, enters their credentials, and lands on their personal dashboard showing their name.
```

## Executable Feature Test

Write one test that:
- Runs end-to-end through the user story (integration/e2e level)
- Asserts the user story outcome directly
- Uses the language and test framework established by `developer:initialize`
- Fails at the start (no implementation exists)

**Scope:** For complex UI features, Page Object abstractions are appropriate. For simple features, keep the test direct and flat.

```typescript
// Example: flat feature test (TypeScript/vitest)
test("returning user logs in and sees dashboard", async () => {
  const { user, session } = await createTestUser({ email: "a@example.com" });
  const response = await app.post("/login", { email: "a@example.com", password: "secret" });

  expect(response.status).toBe(302);
  expect(response.headers.location).toBe("/dashboard");

  const dashboard = await app.get("/dashboard", { session: response.cookies });
  expect(dashboard.text).toContain("Welcome, Alice");
});
```

## Output Artifacts

Save to the session folder (`docs/developer/YYYY-MM-DD-A-<topic>/`):

- `feature-test.md` — user story in plain language plus a copy of the test file path
- Test code in the appropriate project location (per project layout conventions)

Mark `feature-test.md` with `*Draft YYYY-MM-DD*` at the top.

## Stop Condition

After saving both artifacts, tell the user:

> "Feature test written and saved. The test is at `<test-file-path>` and the user story is at `docs/developer/YYYY-MM-DD-A-<topic>/feature-test.md`. Review both, make any changes you want, then remove the `*Draft YYYY-MM-DD*` marker from `feature-test.md`. Start a new session and run `developer:run` (or `developer:planning`) to continue."

Do not write implementation code. Do not run the test to verify it fails (the implementation doesn't exist yet). Do not invoke any other skill.
