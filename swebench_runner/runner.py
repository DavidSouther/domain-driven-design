#!/usr/bin/env python3
"""runner.py -- drive Claude Code headlessly over SWE-bench instances.

For each instance in a local ``instances.jsonl`` (``instance_id``, ``repo``,
``base_commit``, ``problem_statement``): clone the repo, check out
``base_commit`` into an isolated working directory, invoke ``claude -p``
(developer:ailly long-loop mode) inside that checkout, capture the
working-tree diff as ``model_patch``, and append one official SWE-bench
predictions record plus a session-metadata sidecar record.

Usage:
    python3 -m swebench_runner run --instances instances.jsonl \\
        --workdir work --out predictions.jsonl \\
        --metadata-out run_metadata.jsonl --model-name claude-ailly-longloop

Exit codes:
    0  batch completed (individual instance failures are recorded, not raised)
    2  argparse usage error (missing/invalid CLI flags)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_REPO_BASE = "https://github.com/{repo}.git"
# Not exposed as a required CLI flag; a module constant is enough for MVP.
DEFAULT_MAX_TURNS = 40

# The literal developer:ailly long-loop trigger phrasing, verified against
# references/shapes/long-loop.md ("run a long loop", "dynamic workflow", "run
# <project> to completion"): this template hits "long loop" and "to completion".
PROMPT_TEMPLATE = """\
Run a developer:ailly long loop to completion, autonomously, with no draft-gate \
stops, to resolve the following GitHub issue in the repository checked out in the \
current working directory. Do not commit; leave the changes in the working tree.

Issue:
{problem_statement}"""


@dataclass(frozen=True)
class Instance:
    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str


@dataclass(frozen=True)
class ClaudeInvocation:
    """Result of one `claude -p ...` subprocess call."""

    returncode: int
    session_id: str | None
    total_cost_usd: float | None
    error: str | None  # None on success; a human-readable note on any failure mode


def parse_instances(path: Path) -> list[Instance]:
    instances: list[Instance] = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"instances file line {lineno}: invalid JSON: {e}") from e
        try:
            instance = Instance(
                instance_id=data["instance_id"],
                repo=data["repo"],
                base_commit=data["base_commit"],
                problem_statement=data["problem_statement"],
            )
        except KeyError as e:
            raise ValueError(
                f"instances file line {lineno}: missing required field {e}"
            ) from e
        instances.append(instance)
    return instances


def checkout_instance(instance: Instance, repo_base: str, workdir: Path) -> Path:
    """Clone `repo_base.format(repo=instance.repo)` into `workdir/instance.instance_id`
    and check out `instance.base_commit`. Returns the checkout path."""
    source = repo_base.format(repo=instance.repo)
    dest = workdir / instance.instance_id
    _ = subprocess.run(
        ["git", "clone", source, str(dest)], check=True, capture_output=True
    )
    _ = subprocess.run(
        ["git", "-C", str(dest), "checkout", instance.base_commit],
        check=True,
        capture_output=True,
    )
    return dest


def build_prompt(problem_statement: str) -> str:
    """The fixed developer:ailly long-loop prompt template from design.md,
    verified against long-loop.md's trigger phrasing (Step 4)."""
    return PROMPT_TEMPLATE.format(problem_statement=problem_statement)


def invoke_claude(
    checkout: Path, prompt: str, max_turns: int = DEFAULT_MAX_TURNS
) -> ClaudeInvocation:
    """Run `claude -p <prompt> --output-format json --permission-mode acceptEdits
    --max-turns <max_turns>` with cwd=checkout. Never raises on a non-zero exit or
    unparseable stdout; both are folded into ClaudeInvocation.error."""
    try:
        proc = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--output-format",
                "json",
                "--permission-mode",
                "acceptEdits",
                "--max-turns",
                str(max_turns),
            ],
            cwd=checkout,
            capture_output=True,
            text=True,
        )
    except OSError as e:
        return ClaudeInvocation(
            returncode=-1, session_id=None, total_cost_usd=None, error=str(e)
        )

    if proc.returncode != 0:
        return ClaudeInvocation(
            returncode=proc.returncode,
            session_id=None,
            total_cost_usd=None,
            error=f"claude exited {proc.returncode}: {proc.stderr}",
        )

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return ClaudeInvocation(
            returncode=proc.returncode,
            session_id=None,
            total_cost_usd=None,
            error=f"unparseable claude stdout: {e}",
        )

    return ClaudeInvocation(
        returncode=proc.returncode,
        session_id=envelope.get("session_id"),
        total_cost_usd=envelope.get("total_cost_usd"),
        error=None,
    )


def capture_patch(checkout: Path) -> str:
    """`git add -A && git diff --cached` in checkout. Empty string, not an error,
    when there is no change."""
    _ = subprocess.run(
        ["git", "-C", str(checkout), "add", "-A"], check=True, capture_output=True
    )
    result = subprocess.run(
        ["git", "-C", str(checkout), "diff", "--cached"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a") as f:
        _ = f.write(json.dumps(record) + "\n")


def run(args: argparse.Namespace) -> int:
    """Orchestrates parse_instances -> checkout_instance -> build_prompt ->
    invoke_claude -> capture_patch -> append_jsonl(predictions) + append_jsonl(metadata)
    for every instance; a per-instance failure is recorded, not raised, and the
    batch continues."""
    out = Path(args.out)
    metadata_out = Path(args.metadata_out)
    workdir = Path(args.workdir)

    instances = parse_instances(Path(args.instances))
    _ = out.write_text("")
    _ = metadata_out.write_text("")

    for instance in instances:
        patch = ""
        invocation: ClaudeInvocation | None = None
        error: str | None = None

        try:
            checkout = checkout_instance(instance, args.repo_base, workdir)
            prompt = build_prompt(instance.problem_statement)
            invocation = invoke_claude(checkout, prompt)
            patch = capture_patch(checkout)
            error = invocation.error
        except (subprocess.CalledProcessError, OSError) as e:
            error = f"instance {instance.instance_id}: checkout failed: {e}"

        append_jsonl(
            out,
            {
                "instance_id": instance.instance_id,
                "model_name_or_path": args.model_name,
                "model_patch": patch,
            },
        )
        metadata_record = {
            "instance_id": instance.instance_id,
            "session_id": invocation.session_id if invocation else None,
            "total_cost_usd": invocation.total_cost_usd if invocation else None,
        }
        if error is not None:
            metadata_record["error"] = error
        append_jsonl(metadata_out, metadata_record)

    return 0


def grade(args: argparse.Namespace) -> int:
    """Reserved for the Docker-grading stretch goal. Unimplemented in this feature."""
    message = "swebench_runner grade: not implemented yet (deferred, see design.md)"
    print(message, file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swebench_runner",
        description="Drive Claude Code headlessly over SWE-bench instances.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run", help="Produce predictions.jsonl for a batch of instances."
    )
    _ = run_parser.add_argument(
        "--instances", required=True, help="Path to a SWE-bench-shaped instances.jsonl"
    )
    _ = run_parser.add_argument(
        "--repo-base",
        default=DEFAULT_REPO_BASE,
        help="Clone-source template with {repo} substitution",
    )
    _ = run_parser.add_argument(
        "--workdir", required=True, help="Directory to hold per-instance checkouts"
    )
    _ = run_parser.add_argument(
        "--out", required=True, help="Path to write the official predictions.jsonl"
    )
    _ = run_parser.add_argument(
        "--metadata-out",
        required=True,
        help="Path to write the session-metadata sidecar",
    )
    _ = run_parser.add_argument(
        "--model-name", required=True, help="model_name_or_path for predictions records"
    )

    _ = subparsers.add_parser(
        "grade", help="(reserved) grade predictions.jsonl with the Docker harness"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return run(args)
    if args.command == "grade":
        return grade(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
