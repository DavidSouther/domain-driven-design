# Representative Sub-Sample for a First Real Run

`swebench_runner` is deliberately dependency-free and does not fetch instances
itself (see `../.ailly/developer/2026-07-08-A-swebench-runner/design.md`,
Alternatives: "Fetch instances from HuggingFace in-process — rejected for the
MVP"). Before running it for real, a human materializes a local
`instances.jsonl`. This note identifies a small sub-sample to start with and how
to turn it into that file.

## Selection

SWE-bench Lite (`princeton-nlp/SWE-bench_Lite`, 300 instances) draws from about
a dozen repositories. Rather than a random draw from one or two of them, this
sub-sample picks **5 instances across 5 different repositories**, so a first
run's pass/fail says something about breadth of domain rather than one
codebase's idiosyncrasies:

| instance_id | repo | domain |
|---|---|---|
| `django__django-11001` | django/django | web framework (ORM/query layer) |
| `astropy__astropy-6938` | astropy/astropy | scientific computing |
| `scikit-learn__scikit-learn-14983` | scikit-learn/scikit-learn | machine learning |
| `sympy__sympy-20590` | sympy/sympy | symbolic math |
| `pytest-dev__pytest-11143` | pytest-dev/pytest | testing tooling (fixing its own test framework) |

`instance_id`/`repo` pairs above were confirmed directly against the
HuggingFace `datasets-server` `rows` API for `princeton-nlp/SWE-bench_Lite`
(split `test`). This note does **not** transcribe each instance's
`base_commit` or full `problem_statement` by hand — those are long,
exact-sensitive fields, and hand-copying them risks a subtly wrong commit hash
that would silently break a run. Pull them programmatically instead (below).

## Materializing `instances.jsonl`

```bash
pip install datasets
python3 - <<'PY'
import json
from datasets import load_dataset

sample_ids = {
    "django__django-11001",
    "astropy__astropy-6938",
    "scikit-learn__scikit-learn-14983",
    "sympy__sympy-20590",
    "pytest-dev__pytest-11143",
}

ds = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
rows = [r for r in ds if r["instance_id"] in sample_ids]

with open("instances.jsonl", "w") as f:
    for r in rows:
        json.dump(
            {
                "instance_id": r["instance_id"],
                "repo": r["repo"],
                "base_commit": r["base_commit"],
                "problem_statement": r["problem_statement"],
            },
            f,
        )
        f.write("\n")
PY
```

## Running it for real

Once `instances.jsonl` exists, a real run (spends Anthropic API budget, clones
5 real GitHub repos, and requires the real `claude` CLI first on `PATH`):

```bash
python3 -m swebench_runner run \
  --instances instances.jsonl \
  --out predictions.jsonl \
  --metadata-out run_metadata.jsonl \
  --workdir ./runs \
  --model-name claude-ailly-longloop
```

Not run yet as part of this quick loop — the feature test proves the plumbing
hermetically (fake `claude` on `PATH`, per `design.md`). Actually running this
sub-sample for a real pass-rate number is the deliberate next step, done
manually with the human's go-ahead.
