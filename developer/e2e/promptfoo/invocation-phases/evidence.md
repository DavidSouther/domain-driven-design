# Promptfoo Invocation-Phases Evidence

The pilot compares baseline and invocation arms. A release-grade comparison is:

- improved > 0
- regressed == 0

Promptfoo result inspection should preserve these exported fields:

- results.stats
- response.output
- score
- gradingResult.reason
- error
- providerOutput

Observed `npx promptfoo@latest eval` JSON structure:

- `evalId` names the run.
- `results.prompts[]` carries prompt labels and aggregate metrics.
- `results.results[]` carries one row per expanded arm/phase case.
- Each result row carries `vars`, `response.output`, `response.providerOutput`,
  `response.metadata`, `score`, `success`, `gradingResult.reason`, and
  `gradingResult.componentResults[]`.
- Provider metadata is mirrored into the row-level `metadata`, including
  `phaseName`, `armName`, and the role-ordered conversation.
- `results.stats` summarizes successes, failures, errors, duration, and token
  usage.

Conversation evidence is preserved as role-ordered messages and turns:

conversation:
messages:
turns:
  - role: system
    content: "Use the developer e2e profile."
  - role: user
    content: "Run the lifecycle prompt."
  - role: assistant
    content: "A filled response for the selected arm."
  - role: user
    content: "Compare the filled result with the baseline."
  - role: assistant
    content: "A comparison-ready response with provider evidence."

Manual commands:

`npx promptfoo@latest validate config -c developer/e2e/promptfoo/invocation-phases/promptfooconfig.yaml`

`npx promptfoo@latest eval -c developer/e2e/promptfoo/invocation-phases/promptfooconfig.yaml -o /tmp/eval-results.json --no-cache --no-share`

Set `AILLY_PROMPTFOO_BASELINE_RUN_DIR` and
`AILLY_PROMPTFOO_INVOCATION_RUN_DIR` to existing filled Ailly run artifact
directories. Hosted llm-rubric graders need their provider credential
environment variables, and `PROMPTFOO_PYTHON` can select the intended Python
interpreter when the shell default is wrong.

If Promptfoo selects an unintended model-graded assertion provider, pass an
explicit grader on the manual eval command, for example `--grader
openai:gpt-5-mini`, with that grader's credential environment already set.
