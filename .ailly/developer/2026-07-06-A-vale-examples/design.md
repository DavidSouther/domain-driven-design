# Vale-Fix Worked Examples

**Libraries & Skills:** none required (per `research.md`; no Vale agentic skill exists to load — work from Vale's documentation and this repo's existing `scripts/vale-fix.sh`).

## Purpose

`scripts/vale-fix.sh` dispatches a per-file Claude Haiku session to fix Vale findings, giving it only the rule name, message, and line. For rules that don't state a mechanical correction (most of the `DDD` custom style), Claude has to guess a fix from the rule's message alone — and can guess wrong in a way that satisfies one rule while violating another. The observed case: `DDD.PassiveVoice` fires on "This item is mentioned for parity with the sibling skills"; Claude rewrites to "We mention this item for parity with the sibling skills," which fires `Google.We`; fixing that by returning to a passive form re-fires `DDD.PassiveVoice` — a livelock between the two rules that never converges. An editor SME's guidance, reflected in the originating prompt, is that LLMs imitate worked examples more reliably than they satisfy abstract rules. This design gives every Warning/Error rule `vale-fix.sh` dispatches an example a fixer prompt can imitate, and specifically resolves the passive/we loop with an example that satisfies both rules at once.

## Prior Art

- `scripts/vale-fix.sh` — the existing manifest+dispatch pipeline this design extends; already parses `vale --output=JSON` with `jq` per file and shells out to `claude -p`.
- `styles/config/vocabularies/DDD/` — the repo's existing precedent for a `vale sync`-safe local addition living under `StylesPath/config/`; this design's example sidecar files follow the same placement convention.
- Vale's own `substitution`/`existence+action` extension points (`swap:`, `action: {name: replace|edit}`) already encode a bad→good pair for a subset of rules; this design's "auto-derived" tier reads exactly this data out of the JSON `vale-fix.sh` already parses — no new Vale feature needed.
- Confirmed via `research.md`: no existing `--examples` flag, examples database, or third-party plugin does this for Vale; genuinely new work. Full citations in `research.md`/`research/public.md`.

## User Journey and Metrics

Unchanged from today except for what the dispatched Claude session receives:

1. `vale-fix.sh` scans a file and builds its findings manifest exactly as today.
2. New: for each **distinct** rule that fired (once per rule, not once per finding line), the script resolves a worked example in this order — **auto-derived** (from the finding's own `.Match`/`.Action.Params` when the rule is `substitution` or `existence`+`action`) → **sidecar file** (hand-authored or LLM-generated, under `styles/config/examples/`) → nothing (the rule's own message/link still appears in the findings list, as today).
3. The dispatched prompt gains one additional section, "Worked examples for rules seen above," listing each distinct rule's bad/good pair (and note, if present) once.
4. Claude fixes the file using the findings *and* the worked examples. The passive/we loop is expected to resolve because the `DDD.PassiveVoice` and `Google.We` examples both demonstrate naming a concrete actor instead of falling back to a passive construction or "we."

**Metrics:** no runtime metric; this is a prompt-quality change to an internal tool, not a service. Success is directly observable: the two rules that used to loop converge within one dispatch instead of oscillating across repeated `vale-fix`/`vale-check` cycles. Verified by the feature test (one dispatch, one prompt, example appears once) plus manual confirmation against the original `.ailly/prompts/vale_examples` transcript's file.

## Specification

**1. Sidecar schema** — one file per rule, sync-safe under `styles/config/examples/<Style>/<Rule>.examples.yml`:

```yaml
rule: DDD.PassiveVoice
examples:
  - bad: "This item is mentioned for parity with the sibling skills."
    good: "The skill index mentions this item for parity with the sibling skills."
    note: "Name the specific actor — not 'we' — to satisfy both active voice and Google.We."
```

**2. Hand-authored seed** (ships with this feature, resolves the motivating loop) — two files, both teaching the same target rewrite from the two different sides of the loop:

- `styles/config/examples/DDD/PassiveVoice.examples.yml` — `bad` is the original passive sentence from the transcript; `good` names the concrete actor.
- `styles/config/examples/Google/We.examples.yml` — `bad` is the transcript's own first "fix" ("We mention this item for parity with the sibling skills."); `good` is the same actor-named rewrite.

**3. LLM-generated tier (offline, this design's larger share of work):** a new script, `scripts/vale-generate-examples.sh`, iterates every rule at `warning` or `error` level across the repo's effective style set (`Google`, `Joblint`, `DDD` — `.vale.ini`'s `BasedOnStyles`), skipping:

- any rule already covered by the auto-derived tier (has a `swap:` map or an `action:` block — nothing to generate),
- any rule that already has a hand-authored sidecar (the two seed files above — the generator never overwrites curated content),

and for everything else, dispatches one LLM call per rule (mirroring `vale-fix.sh`'s own `xargs -P 8` parallel-dispatch pattern), giving it the rule's own YAML body and asking it to either (a) write a `bad`/`good`/`note` example in the schema above, or (b) emit nothing when the rule's own `message:`/`link:` already states a sufficient correction on its own. Output is written to the sidecar path and reviewed/committed like any other content change — never generated or trusted at fix-time.

**4. `vale-fix.sh` changes:**

- Add a `jq` dedup pass (`[.[$f][].Check] | unique`) so each distinct rule contributes one manifest entry regardless of how many lines it fired on.
- For each distinct rule, resolve an example via the lookup order below and append a "Worked examples" section to the per-file prompt.
- Add a `VALE_FIX_DRY_RUN` escape hatch: when set, print the assembled prompt for each flagged file to stdout instead of invoking `claude -p`, so the prompt-assembly logic is directly testable without a network/LLM call.

**5. Lookup order, precisely:** auto-derived (computed fresh per run from that run's own JSON `.Match` + `.Action.Params[0]`, never cached) → sidecar file (hand-authored or LLM-generated — same schema, same lookup, no distinction at read time) → nothing (existing findings list still names the rule and its message/link).

## Alternatives

- **Native Vale `--examples` flag / Go fork / `--output=template`.** Rejected — `research.md` confirms `vale --output=JSON` (already parsed by `vale-fix.sh`) carries everything needed; forking Vale or learning its Go template system would be strictly more work for the same result.
- **Read `swap`/`action` live from style YAML at report time instead of the JSON output.** Rejected — the JSON `vale-fix.sh` already parses carries the matched text and its replacement directly; re-parsing YAML would duplicate data already in hand.
- **Generate LLM examples on-the-fly at fix-time instead of an offline script.** Rejected (user decision) — bakes non-deterministic, unreviewed content into every fix run and adds LLM latency/cost to the hot path; an offline, reviewed, committed generation step keeps `vale-fix.sh` itself fast and deterministic.
- **Surface examples in `vale-check.sh`'s human-facing output too.** Deferred — this design targets only `vale-fix.sh`'s Claude-facing prompt (resolved in `research.md`'s draft-gate review).

## Summary

Extends `vale-fix.sh` with a worked-example lookup (auto-derived from Vale's own JSON output, or a `styles/config/examples/` sidecar) appended once per distinct rule to each dispatched fix prompt, plus a `VALE_FIX_DRY_RUN` hook for testing it without a live LLM call. Ships two hand-authored examples that resolve the motivating `DDD.PassiveVoice` ⇄ `Google.We` livelock, and a new offline `scripts/vale-generate-examples.sh` that backfills the remaining Warning/Error rules across `Google`, `Joblint`, and `DDD`, skipping any rule an example would add no value to.

### Deferred technical decisions

- Whether the LLM-generated tier should be periodically regenerated (e.g., re-run whenever `vale sync` updates a package's rule bodies) or is a one-time backfill — left to whoever runs `scripts/vale-generate-examples.sh` next; the script is idempotent (skips rules that already have a sidecar) so re-running it is always safe.
- No formal termination guarantee for the fixer loop in general — worked examples mitigate known loops; a novel two-rule conflict without an authored example could still oscillate.

## The Feature Test

**User story:** A file trips `DDD.PassiveVoice` on two separate lines. When `vale-fix.sh` builds that file's fix prompt, the `DDD.PassiveVoice` worked example appears in the prompt exactly once, teaching Claude the actor-naming escape instead of leaving Claude to guess a fix that flips into `Google.We`.

**Test path:** `developer/tests/test_vale_fix_examples.py`

**Runs today:** `python3 developer/tests/test_vale_fix_examples.py` — writes a probe file that trips `DDD.PassiveVoice` on two lines, then runs `scripts/vale-fix.sh <probe file>` twice: once with `VALE_FIX_DRY_RUN=1` and once without. Never risks a live dispatch regardless of implementation: for the whole run, it shadows the `claude` binary on `PATH` with a no-op stub that only logs that it was called, so even a missing or partially-wired dry-run hook cannot reach a real LLM call.

**Asserts:**

- With `VALE_FIX_DRY_RUN=1`: the `claude` stub is never called, and the printed prompt contains a "Worked examples" section with the `DDD.PassiveVoice` bad/good/note text from `styles/config/examples/DDD/PassiveVoice.examples.yml` exactly once, even though the probe file trips the rule on two separate lines.
- Without `VALE_FIX_DRY_RUN` set: the script still exits cleanly and the `claude` stub is called exactly once, confirming the new hook doesn't break the default dispatch path (for example, by referencing an unset variable under the script's `set -u`).

It currently fails (red) because `vale-fix.sh` has neither the dedup pass, the lookup, the prompt section, nor the `VALE_FIX_DRY_RUN` hook, and `styles/config/examples/DDD/PassiveVoice.examples.yml` does not exist yet.

**Coverage boundary (acknowledged, not tested here):** the probe's rule has no `swap`/`action` to auto-derive from, so this test exercises only the sidecar branch of the lookup order in Specification item 5. The auto-derived branch, the "nothing" fallback, the LLM-generated tier, and `styles/config/examples/Google/We.examples.yml` are part of this design but are validated by code review and manual verification against the original transcript, not by this one feature test.
