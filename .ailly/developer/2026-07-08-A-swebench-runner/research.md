# SWE-bench Runner with Claude Code Long-Loop

## Topic and Intent

> Build a tool that runs SWE-bench task instances, where each task is solved by driving Claude Code headlessly through `developer:ailly`'s long-loop mode, to get a real SWE-bench pass-rate number by actually running Claude Code against SWE-bench issues.

The goal is to scaffold an autonomous workflow that accepts a SWE-bench task instance (repository, problem statement, base commit) and runs Claude Code in long-loop mode (no human draft-gate stops) to generate a patch, then grades that patch against the official SWE-bench evaluation harness.

## Search/Expand

### SWE-bench Dataset and Evaluation

SWE-bench is a benchmark of real GitHub issues paired with their solutions. Datasets live on Hugging Face (primary variants: `princeton-nlp/SWE-bench_Lite` for testing, `SWE-bench/SWE-bench_Verified` for official). Each task instance contains:

- **instance_id** (string): unique identifier like `"owner__repo-pr_number"`
- **repo** (string): owner/name format
- **base_commit** (string): the repository HEAD before the solution PR
- **problem_statement** (string): the issue description
- **patch** (string): the gold solution (should be hidden when solving)
- **test_patch** (string): test modifications included in the solution
- **FAIL_TO_PASS** (list): test cases that must transition from failing to passing
- **PASS_TO_PASS** (list): test cases that must remain passing
- **created_at** (string): metadata timestamp

The official SWE-bench evaluation harness expects predictions in JSONL format, with each line containing:
- **instance_id**: task identifier
- **model_name_or_path**: model identifier string
- **model_patch**: patch content as a plain string

The harness applies patches in Docker containers, runs tests, and reports per-instance pass/fail and aggregate resolution rate.

### Claude Code Headless Invocation

Claude Code supports non-interactive execution via the `-p` (or `--print`) flag, read-only by default, with built-in support for structured output and cost tracking:

- **Basic invocation**: `claude -p "prompt here"` runs a single pass and exits
- **Bare mode**: `--bare` flag skips auto-discovery of hooks, skills, MCP servers; recommended for CI/scripted use
- **Output format**: `--output-format json` returns structured JSON with `session_id`, `total_cost_usd`, and `result` fields
- **Tool approval**: `--allowedTools "Read,Edit,Bash"` pre-approves specific tools; `--permission-mode acceptEdits` pre-approves filesystem writes
- **Turn limits**: `--max-turns N` caps agentic iterations (useful to prevent unbounded runs)
- **Streaming**: `--output-format stream-json` with `--verbose` and `--include-partial-messages` for real-time token streaming
- **Continuation**: `--continue` resumes the most recent session; `--resume session_id` resumes a specific one

To invoke long-loop mode for an individual task, pass a prompt that references the task ("fix this issue") and the developer:ailly long-loop mode will auto-activate (phrasing like "run a long loop", "dynamic workflow", or "run to completion" triggers it). The long-loop mode runs Research, Design, Plan, Build, and Cleanup phases through isolation, with automatic draft-gate resolution (a research-and-decide reviewer decides gate open questions rather than halting for human review).

**Session output**: When using `--output-format json`, the response includes `session_id` (reusable across `--continue` calls) and `total_cost_usd` (per-model cost breakdown), enabling tracking of spend per SWE-bench instance solved.

### Repo Conventions

- **Commit style**: Conventional Commits (observed: `chore: release X.Y.Z`, `feat: ...`, `bug: ...`, `feat(scope): description (#issue)`)
- **Python tooling**: ruff for linting, pytest for test execution (configured in `.github/scripts/pyproject.toml`)
- **E2E structure**: Familiar pattern across plugins: `e2e/assemblies/`, `e2e/evals/`, `e2e/evals/scripts/check_*.py`; root `e2e/` uses static checkers (no model needed), plugin `e2e/` uses model-driven transcripts
- **Python execution**: Repo uses `python3` as the global executable (documented in user global CLAUDE.md)

### Libraries & Skills

**Before doing any work in this feature, load these skills via the active harness's skill-loading mechanism:**

- `developer:ailly` — the five-phase development coordinator. The long-loop mode is invoked by declaring it at session start (phrasinglike "run a long loop") and is documented in `references/shapes/long-loop.md`. Passing a prompt like "use developer:ailly long-loop to solve this SWE-bench task" will trigger long-loop behavior, with auto-clearing of draft gates via a research-and-decide reviewer.

**No other library skills are required.** The headless invocation is driven via Claude Code CLI (`claude -p`), which is a standard tool; no custom MCP server or agent is needed for the basic invocation pattern.

## Falsification/Refine

This is a single, well-scoped feature: build a harness tool that orchestrates invoking Claude Code in long-loop mode for each SWE-bench instance and collecting the results. The surface is:

1. Accept a SWE-bench instance (via HuggingFace dataset, instance_id, or local repo path)
2. Invoke `claude -p "run a long loop to solve this SWE-bench task"` headlessly with the task description, code context, and test expectations
3. Extract the generated patch from Claude Code's session output (via `--output-format json` and `session_id`)
4. Write predictions.jsonl entries (one per instance)
5. (Stretch goal) Run the official `swebench` harness to grade predictions

The scope is **feature-sized** but the feature test will be narrow: run against 1–3 SWE-bench Lite instances end-to-end, extract patches, and verify they match expected format (don't require Docker grading in the quick-loop feature test).

## Scope

### In
- Harness scaffolding: accept SWE-bench instances, invoke Claude Code in long-loop mode, collect patches
- Session tracking: capture session_id and total_cost_usd for each run
- Predictions output: generate JSONL in the official SWE-bench format (instance_id, model_name_or_path, model_patch)
- Python CLI or utility to orchestrate invocations
- Unit tests for parsing, JSONL generation, edge cases
- E2E test: run against 1–3 Lite instances and verify patch extraction

### Out (for this quick-loop feature test)
- Docker-based official SWE-bench evaluation (marked as a stretch goal; Design should decide if it's feasible within quick-loop scope)
- Cost optimization, caching, or retries
- Multi-worker parallelization (can be added later if needed)
- Integration with a CI/CD system or task queue

### Open Questions for Design
1. **Docker grading in feature test scope?** Running the official `swebench harness.run_evaluation` inside the feature test requires Docker + Python `swebench` package; is this too heavy for a quick-loop or should it be a separate integration step after the feature test passes?
2. **Prompt engineering for long-loop?** What prompt should be passed to Claude Code to best frame a SWE-bench task for long-loop mode? Should the prompt include hints (test lists, error messages) or only the issue statement?
3. **Claude Code invocation architecture?** Should the harness spawn `claude -p` via subprocess, use the Claude Code Python SDK directly (if available), or call the Agent SDK?
4. **Single-instance vs. batch?** Should the MVP harness tool accept a single instance ID and run once, or a batch file (list of IDs) and run multiple in sequence?

## Resolved Decisions

None at this stage — research phase does not resolve architecture decisions. The open questions above are for Design to address.

## Sources

- [SWE-bench Dataset Guide - Hugging Face](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite)
- [SWE-bench Datasets Reference](https://www.swebench.com/SWE-bench/guides/datasets/)
- [SWE-bench Evaluation Guide](https://www.swebench.com/SWE-bench/guides/evaluation/)
- [Run Claude Code Programmatically - Claude Code Docs](https://code.claude.com/docs/en/headless)
- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [developer:ailly Long-Loop Mode Reference](https://www.swebench.com/SWE-bench/references/shapes/long-loop.md) (note: actual path is in this repo at `developer/skills/ailly/references/shapes/long-loop.md`)
- [E2E Testing Convention - This Repository](https://github.com/davidsouther/domain-driven-design/tree/main/e2e)
