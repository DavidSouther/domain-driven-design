I am running this development session as a **long loop** (a dynamic workflow, run
to completion autonomously) for the `token-bucket-rate-limiter` topic.

The session folder `.ailly/developer/2026-06-17-A-token-bucket-rate-limiter/`
contains `research.md`, and that file still has `*Draft 2026-06-17*` at the top —
nobody has removed it. Its closing section reads:

> ## Resolved Decisions
>
> Resolved by the research:
>
> - Use a monotonic clock source, not wall-clock, for refill timing.
>
> Open questions:
>
> 1. Per-key bucket eviction: TTL sweep vs. LRU cap. Memory grows unbounded if
>    idle keys are never evicted.
> 2. Refill granularity: refill on every request (lazy) vs. a background ticker.

There is no design doc or feature test in the folder yet.

Do not try to read the filesystem — the folder's state is exactly as described
above. We are in a long loop, so do not stop and wait for me at this gate. Carry
the loop forward from here and show me what happens at this draft gate.
