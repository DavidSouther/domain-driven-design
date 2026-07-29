# Code Mode Thresholds: Quick Reference

Code Mode scripts are appropriate for a task that will run a handful of times (3 to 8), with minor
input variation. A true one-off favors a direct LLM pass; a task that runs
indefinitely often is a full feature. One question decides the rest:
can the LLM both perform the task and verify its own answer? Where no, script it at the first run. Where yes, cost and the 3-to-8 rerun band decide. Weigh
three angles below. When a task carries judgment a script cannot encode,
neither pure LLM nor pure script suffices: split the work (Angle 3).

## Angle 1: Source Materials

| Band | Rough total | Direct-LLM verdict |
| --- | --- | --- |
| Trivial | 1 to 2 files, under ~20K tokens | Fits comfortably, no reliability concern. |
| Small | a handful of files, tens of thousands of tokens | Direct by default; script only if the format is clean and it reruns. |
| Moderate | many or large files, ~100K to 500K tokens | Code Mode is appropriate on input cost and on "lost in the middle" reliability. |
| Large | exceeds the context window, or too many files to hold at once | Cannot be done in one direct pass. Code Mode, or a script-plus-LLM hybrid, at one run. |

Structure matters as much as size: clean CSV/JSON favors a script at any
volume or rerun; semi-structured logs favor authoring a parser once; freeform
prose needing interpretation favors a direct pass or the hybrid in Angle 3.

Wrong turn: a brittle parser over messy prose fails silently. An LLM pass
over large clean input drops mid-context records without flagging it.

## Angle 2: The Dataset

Volume after extraction, not source size (a small query can return 50K rows).

| Band | Rough size | Direct-LLM verdict |
| --- | --- | --- |
| Trivial | a few values, a handful of rows | Reliable and instant. |
| Small | tens of rows, a few columns | Borderline: exact arithmetic across dozens of numbers starts to accumulate error. |
| Moderate | hundreds to low thousands of rows | Code Mode on correctness: exact counting, summing, and grouping become unreliable regardless of cost. |
| Large | tens of thousands of rows, or more than fits in context | Code Mode on feasibility: the data must be reduced before it reaches the model. |

LLMs are not calculators: exact counts and sums degrade with volume, with no
self-check when the total is wrong.

Wrong turn: a direct pass at volume yields confident, silently-wrong
aggregates. A script at trivial volume is just overkill.

## Angle 3: The Task / Computation

| Band | Examples | Verdict |
| --- | --- | --- |
| Trivial op | single lookup, reformat, extract one value | Direct LLM. |
| Simple aggregate | sum, count, min/max, group-by | Unreliable at volume; script once there is any real row count. |
| Multi-step transform | joins, pivots, multi-stage filters, exact-key dedup | Code Mode strongly favored even at n=1: error-prone and unverifiable by hand. |
| Statistical / numeric-heavy | regression, correlation, optimization, simulation, FFT | Code Mode mandatory at n=1: a capability limit, not a cost question. |
| Judgment-heavy text ops | fuzzy matching, entity resolution, messy-name normalization | Hybrid: a script cannot capture the judgment, and an LLM cannot scale the mechanical pass. |

Wrong turn: a direct pass on real computation emits a plausibly formatted,
fabricated result. A pure script on a genuinely fuzzy task over- or
under-merges silently.

## Cost Grounding

Claude API list pricing, July 2026 snapshot verified against provider
documentation, per 1M tokens:

| Model | Input ($/1M) | Output ($/1M) | Context |
| --- | --- | --- | --- |
| Haiku 4.5 | $1 | $5 | 200K |
| Sonnet 5 / 4.6 | $3 | $15 | 1M |
| Opus 5 | $5 | $25 | 1M |
| Fable 5 | $10 | $50 | 1M |

| Input size | Haiku | Sonnet | Opus | Fable |
| --- | --- | --- | --- | --- |
| Small (~10K in, ~500 out) | $0.01 | $0.04 | $0.06 | $0.13 |
| Large (~500K in, ~1K out) | n/a (over 200K ctx) | $1.52 | $2.53 | $5.05 |

Authoring a script once: about $0.30 (Opus, typical small input) to $1.00
(Opus, large input, which needs a bigger sample to debug against). Running
the finished script again costs near $0. Break-even: about 5 runs for small
clean input on Opus, inside the 3-to-8 band and genuinely ambiguous; under 1
run for large input, where the script wins before the first rerun. Batch API
halves every figure; prompt caching cuts repeated-prefix input to about 0.1x.

## Worked Examples

| Case | Deciding axis | Verdict |
| --- | --- | --- |
| Summing a dataset vs. a regression on dataset | Task complexity | Sum: script past a few dozen rows. Regression: script at any size, no cost argument needed. |
| Column data extracted from logs | Source structure and dataset volume together | Script: semi-structured parsing and row volume both favor it; parameterize the date range and rerun. |
| Dense data in a spreadsheet or database | Dataset volume; source size is a red herring | Script: a single SQL query the LLM writes is itself the win. The data never touches the context window. |
| Complex text operations across files | Source and task complexity together | Hybrid: script the deterministic bulk, LLM adjudicates the ambiguous residual. |

## Rule of Thumb

Reach for Code Mode the moment any one axis crosses from "the LLM can do this
and check its own work" into "it cannot": a source that will not reliably fit
in context, a dataset past a few dozen rows you must count or sum exactly, or
a computation beyond a simple aggregate. Cost decides only when all three
axes are small, clean, and simple; there, the 3-to-8 rerun band tips the
trade-off toward scripting. When judgment is irreducible, split the work
rather than choosing a side. The tie-breaker is never run count. It is
whether the LLM can verify its own answer.

This reference is the detailed backing for the trigger test in
`code-mode.md`'s "When Code Mode Applies" section; read that section first
for the one-line decision rule this expands on.
