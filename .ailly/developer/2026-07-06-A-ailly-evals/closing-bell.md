# Closing Bell: Ailly Evals — Production-Ready Eval Harness

*Written 2026-07-06.*
*Study plan, scheduled and executed once near project completion.*

## Participant Profile

A developer competent with Rust and CLI tools generally — comfortable installing dependencies, running `cargo`, reading a CLI's `--help`, and following a project's README — but with **no prior exposure to `ailly_two` itself**.
They have not used its CLI, read `DESIGN.md`, or seen the `ailly-skill-eval` method before this study, and are not assumed to already understand assemblies, conversations, evaluation suites, or the assertion palette.
Only general software-engineering competence is assumed; `ailly_two`'s own conceptual model is knowledge they must build during the study from the provided documentation, the way a new contributor picking up the project cold would.
They also have not read this design doc, its plan, or watched the author use any capability this project adds — nothing about `ailly_two`, old or new, is prior knowledge.
No walkthrough from the author is given at any point during the study.

## Setup and Materials

- A fresh checkout of `ailly_two` at the point this project's features have all landed (behind whatever release-flagging decision Feature-specification settles on — see design.md).
- `.env` populated with credentials for all four providers (Anthropic, OpenAI, Gemini, Bedrock/AWS).
- Available documentation: `DESIGN.md`, `ailly-skill-eval/SKILL.md` and its `references/method.md`, each suite's `README.md`, and whatever this project's own feature-steps produce as their documentation deliverable (CLI `--help` text, the judge-calibration report, the runner-matrix status output).
  This documentation **is** part of the deliverable under test — the participant may read it, and since they arrive with no prior exposure to `ailly_two`, they are expected to.
- An untimed orientation period, up to 15 minutes, immediately before the timed tasks begin: the participant reads `DESIGN.md` and `ailly-skill-eval/SKILL.md` unassisted, to build a working model of assemblies, conversations, evaluation suites, and the assertion palette before attempting any task.
  This reading time is not counted against any task's time-on-task budget below — the budgets measure applying the model, not acquiring it.
- Deliberately withheld: the author is not present, does not answer questions, and does not demonstrate any command during the session.

## Task Scenarios

Stated as the participant's goal, not as steps to operate:

1. **Fast local iteration.**
   "You just edited one skill's `SKILL.md`.
   Find out whether you broke that skill's discovery or invocation, without running the entire suite." *(Critical — Feature A)*
2. **Add a Bedrock model.**
   "Your team wants to try `Llama 4 Scout` on Bedrock in the eval harness.
   Get it running and confirm it completes a real response." *(Critical — Feature B, C)*
3. **Release-readiness check.**
   "Before shipping, confirm every model your team cares about — the full list from `domain-driven-design#29` — actually works end-to-end across all four providers." *(Critical — Feature C, D)*
4. **Trusting a judge verdict.**
   "One of your suites uses an LLM `judge` assertion to grade a subjective response.
   You're not sure whether to trust its pass/fail calls.
   Find out how much you should trust it." *(Critical — Feature E)*
5. **Is this regression real?**
   "You ran the same suite before and after a change and got different pass/fail counts.
   Decide whether that's a real regression or noise." *(Secondary — Feature F, stretch)*
6. **Trusting the method itself.**
   "You're about to build a new eval suite for a skillset using `ailly_two`'s documented method.
   Before you invest in it, find out whether its central claim — that a baseline arm proves a skill earns its place — actually holds up in practice today." *(Secondary — Feature G)*

## Acceptance Criteria

Per task, evaluated against:

- **Task completion.**
  Did the participant reach a correct, defensible answer/outcome using only the provided materials — no author intervention?
- **Time on task.**
  Critical tasks (1–4): completed within 10 minutes each.
  Secondary tasks (5–6): within 15 minutes each.
- **Errors.**
  No more than one wrong command or misread before the participant self-corrects via `--help` or the provided docs, for critical tasks.
- **Ease/satisfaction.**
  A single-question ease rating (1–5) immediately after each task; critical tasks must average ≥4/5 across all critical tasks combined.

## Critical vs. Secondary

**Critical (must pass for the project to land):** Tasks 1–4, corresponding to Features A, B, C, D, E — the core "change something and trust the signal, across every provider" story.

**Secondary (inform the result without blocking it):** Tasks 5–6, corresponding to Features F (stretch) and G (a verification step whose value is confidence, not a new capability).
A weak result on these should be recorded and may motivate follow-up work via `TASKS.md`, but does not by itself fail the Closing Bell.
