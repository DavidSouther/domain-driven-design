I am running this development session as **Code Mode** (the condensed
`developer:ailly` loop for a small standalone script) for the
`todo-sweep` topic.

The ask, verbatim:

> Write a script that finds every `TODO` comment across the repo and, for
> each file that has one, starts a dedicated Claude session using
> `haiku-4.5` with no agents or tool access to resolve them. Cap
> concurrency at 5 outstanding sessions.

There is no session folder yet for this topic. Do not try to read the
filesystem — nothing exists on disk for `todo-sweep`; treat this as a cold
start.

Run this as Code Mode, not the standard five-phase loop and not quick-loop.
Show me what you do first, and how you handle anything in the ask that
isn't fully pinned down.
