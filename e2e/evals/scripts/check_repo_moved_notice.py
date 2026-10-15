#!/usr/bin/env python3
"""Feature test: a legacy install learns that Ailly moved and can be repointed.

User story:
Given a user whose Claude Code, Codex, and pi installs of Ailly come from the
legacy davidsouther/domain-driven-design repository, when a Claude Code
session starts, then the general plugin's SessionStart hook tells the user
that Ailly moved to davidsouther/ailly and tells the agent to offer the
bundled migration script. When the agent runs that script with no flags, it
prints the exact commands that repoint each harness and changes nothing.
With --apply, it runs exactly those commands. The developer and general
plugins ship the notice as release 2026.09.3, which the successor's CalVer
sequence never produces.

The harness CLIs are stubs first on a restricted PATH, with HOME in a
temporary directory, so this test never reads or changes real harness
configuration. Each stub logs its calls, answers only the read-only commands
named in design.md, and rejects any other read.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import AILLY_DIR, REPO, fail, read  # noqa: E402

GENERAL = REPO / "general"
HOOKS = GENERAL / "hooks" / "hooks.json"
SCRIPT = GENERAL / "scripts" / "migrate-to-ailly.py"
DESCRIBED_SKILLS = [
    AILLY_DIR / "SKILL.md",
    GENERAL / "skills" / "using-general" / "SKILL.md",
]

SUCCESSOR = "davidsouther/ailly"
FINAL_VERSION = "2026.09.3"
NOTICE_PLUGINS = ["developer", "general"]
UNCHANGED_VERSIONS = {
    "patterns": "2026.08.2",
    "domain": "2026.08.1",
    "research": "2026.08.1",
    "characters": "2026.06.8",
}

MUTATING = {"add", "remove", "rm", "install", "i", "uninstall", "update", "upgrade", "enable", "disable"}

CLAUDE_PLAN = [
    "claude plugin marketplace remove ailly",
    "claude plugin marketplace add davidsouther/ailly",
    "claude plugin install developer@ailly --scope user",
    "claude plugin install general@ailly --scope user",
    "claude plugin disable general@ailly --scope user",
    "claude plugin install research@ailly --scope project",
]
CODEX_PLAN = [
    "codex plugin remove developer@ailly",
    "codex plugin remove general@ailly",
    "codex plugin marketplace remove ailly",
    "codex plugin marketplace add davidsouther/ailly",
    "codex plugin add developer@ailly",
    "codex plugin add general@ailly",
]
PI_PLAN = [
    "pi remove git:github.com/davidsouther/domain-driven-design",
    "pi install git:github.com/davidsouther/ailly",
]
# (earlier, later) index pairs within each plan that must hold.
PLAN_ORDER = {
    "claude": (CLAUDE_PLAN, [(0, 1), (1, 2), (1, 3), (1, 5), (3, 4)]),
    "codex": (CODEX_PLAN, [(0, 2), (1, 2), (2, 3), (3, 4), (3, 5)]),
    "pi": (PI_PLAN, [(0, 1)]),
}
FOREIGN_COMMANDS = [
    "install code-review@",
    "codex plugin remove documents@",
    "codex plugin add documents@",
    "pi remove npm:pi-unrelated-package",
    "pi remove /",
]

STUB = """#!@PYTHON@
import json, os, sys
from pathlib import Path

MUTATING = @MUTATING@
name = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ["STUB_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps({"bin": name, "argv": args, "cwd": os.getcwd()}) + "\\n")
fixtures = json.loads(Path(os.environ["STUB_FIXTURES"]).read_text(encoding="utf-8"))
key = " ".join(args)
if key in fixtures.get(name, {}):
    sys.stdout.write(fixtures[name][key])
    sys.exit(0)
if MUTATING & set(args):
    sys.exit(0)
sys.stderr.write("stub " + name + ": unsupported read-only command: " + key + "\\n")
sys.exit(2)
"""


def claude_plugin(plugin_id: str, scope: str, enabled: bool, project: Optional[Path] = None) -> dict:
    entry = {
        "id": plugin_id,
        "version": "2026.09.0",
        "scope": scope,
        "enabled": enabled,
        "installPath": f"/stub/.claude/plugins/cache/{plugin_id}",
        "installedAt": "2026-09-01T00:00:00.000Z",
        "lastUpdated": "2026-09-01T00:00:00.000Z",
    }
    if project is not None:
        entry["projectPath"] = str(project)
    return entry


def codex_plugin(name: str, marketplace: str, source: str) -> dict:
    return {
        "pluginId": f"{name}@{marketplace}",
        "name": name,
        "marketplaceName": marketplace,
        "version": "2026.09.0",
        "installed": True,
        "enabled": True,
        "source": {"source": "local", "path": f"/stub/.codex/.tmp/marketplaces/{marketplace}/{name}"},
        "marketplaceSource": {"sourceType": "git", "source": source},
        "installPolicy": "AVAILABLE",
        "authPolicy": "ON_INSTALL",
    }


def fixtures(repo_slug: str, pi_source: str, project: Path) -> dict:
    marketplaces = [
        {"name": "ailly", "source": "github", "repo": repo_slug, "installLocation": "/stub/marketplaces/ailly"},
        {
            "name": "claude-plugins-official",
            "source": "github",
            "repo": "anthropics/claude-plugins-official",
            "installLocation": "/stub/marketplaces/claude-plugins-official",
        },
    ]
    claude_plugins = [
        claude_plugin("developer@ailly", "user", True),
        claude_plugin("general@ailly", "user", False),
        claude_plugin("research@ailly", "project", True, project),
        claude_plugin("code-review@claude-plugins-official", "user", True),
    ]
    git_url = f"https://github.com/{repo_slug}.git"
    codex_plugins = {
        "installed": [
            codex_plugin("developer", "ailly", git_url),
            codex_plugin("general", "ailly", git_url),
            codex_plugin("documents", "openai-primary-runtime", "/stub/runtime"),
        ],
        "available": [],
    }
    pi_list = (
        "User packages:\n"
        f"  {pi_source}\n"
        f"    /stub/.pi/agent/git/{pi_source.removeprefix('git:')}\n"
        "  npm:pi-unrelated-package\n"
        "    /stub/.pi/agent/npm/pi-unrelated-package\n"
    )
    return {
        "claude": {
            "plugin marketplace list --json": json.dumps(marketplaces),
            "plugin list --json": json.dumps(claude_plugins),
        },
        "codex": {"plugin list --json": json.dumps(codex_plugins)},
        "pi": {"list": pi_list},
    }


LEGACY = ("davidsouther/domain-driven-design", "git:github.com/davidsouther/domain-driven-design")
MIGRATED = ("davidsouther/ailly", "git:github.com/davidsouther/ailly")


class Sandbox:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.bin = root / "bin"
        self.bin.mkdir()
        self.home = root / "home"
        self.home.mkdir()
        self.project = root / "project"
        self.project.mkdir()
        self.log = root / "calls.jsonl"
        self.fixtures = root / "fixtures.json"
        stub = STUB.replace("@PYTHON@", sys.executable).replace("@MUTATING@", repr(MUTATING))
        for name in ("claude", "codex", "pi"):
            self._executable(name, stub)
        self._executable("python3", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')

    def _executable(self, name: str, text: str) -> None:
        path = self.bin / name
        path.write_text(text, encoding="utf-8")
        path.chmod(0o755)

    def use(self, state: tuple[str, str]) -> None:
        self.fixtures.write_text(json.dumps(fixtures(state[0], state[1], self.project)), encoding="utf-8")
        self.log.write_text("", encoding="utf-8")

    def env(self) -> dict:
        return {
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "HOME": str(self.home),
            "STUB_LOG": str(self.log),
            "STUB_FIXTURES": str(self.fixtures),
            "CLAUDE_PLUGIN_ROOT": str(GENERAL),
        }

    def calls(self) -> list[dict]:
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line.strip()]

    def run(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            args, cwd=self.root, env=self.env(), capture_output=True, text=True, timeout=60
        )


def mutating_calls(calls: list[dict]) -> list[dict]:
    return [c for c in calls if MUTATING & set(c["argv"])]


def command_line(lines: list[str], command: str) -> Optional[int]:
    pattern = re.compile(r"(?<!\S)" + re.escape(command) + r"(?!\S)")
    for index, line in enumerate(lines):
        if pattern.search(line):
            return index
    return None


def check_hook(box: Sandbox) -> Optional[str]:
    if not HOOKS.is_file():
        return "missing general/hooks/hooks.json (no Claude Code SessionStart notice)"
    try:
        groups = json.loads(read(HOOKS)).get("hooks", {}).get("SessionStart", [])
    except json.JSONDecodeError as error:
        return f"general/hooks/hooks.json is not valid JSON: {error}"
    commands = []
    for group in groups:
        matcher = group.get("matcher") or ""
        if matcher not in ("", "*") and not re.fullmatch(f"(?:{matcher})", "startup"):
            continue
        commands += [h["command"] for h in group.get("hooks", []) if h.get("type") == "command"]
    if not commands:
        return "general/hooks/hooks.json declares no SessionStart command hook for `startup`"

    box.use(LEGACY)
    messages, contexts = [], []
    for command in commands:
        try:
            result = box.run(["/bin/bash", "-c", command])
        except subprocess.TimeoutExpired:
            return f"SessionStart hook timed out: {command}"
        if result.returncode != 0:
            return f"SessionStart hook exited {result.returncode}: {result.stderr.strip()[:160]}"
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            return f"SessionStart hook stdout is not one JSON object: {result.stdout.strip()[:160]!r}"
        messages.append(str(output.get("systemMessage", "")))
        specific = output.get("hookSpecificOutput", {})
        if specific.get("hookEventName") == "SessionStart":
            contexts.append(str(specific.get("additionalContext", "")))
    if box.calls():
        return "SessionStart hook must not call a harness CLI"
    if not any(SUCCESSOR in m for m in messages):
        return f"SessionStart systemMessage must tell the user Ailly moved to {SUCCESSOR}"
    context = "\n".join(contexts)
    for needle, reason in [
        (SUCCESSOR, f"must name {SUCCESSOR}"),
        (str(SCRIPT), f"must name the migration script by absolute path {SCRIPT}"),
        ("--apply", "must say the script changes configuration only with --apply"),
    ]:
        if needle not in context:
            return f"SessionStart additionalContext {reason}"
    return None


def check_plan_order(lines_or_calls: list[str], where: str) -> Optional[str]:
    for harness, (plan, order) in PLAN_ORDER.items():
        positions = [command_line(lines_or_calls, command) for command in plan]
        for command, position in zip(plan, positions):
            if position is None:
                return f"{where}: missing {harness} command `{command}`"
        for earlier, later in order:
            if positions[earlier] >= positions[later]:  # type: ignore[operator]
                return f"{where}: `{plan[earlier]}` must come before `{plan[later]}`"
    return None


def check_dry_run(box: Sandbox) -> Optional[str]:
    if not SCRIPT.is_file():
        return f"missing {SCRIPT.relative_to(REPO)} (no migration script)"

    box.use(LEGACY)
    result = box.run([sys.executable, str(SCRIPT)])
    if result.returncode != 0:
        return f"dry run exited {result.returncode}: {(result.stderr or result.stdout).strip()[:160]}"
    lines = result.stdout.splitlines()
    reason = check_plan_order(lines, "dry run plan")
    if reason:
        return reason
    research = command_line(lines, CLAUDE_PLAN[5])
    if research is not None and str(box.project) not in lines[research]:
        return "dry run plan must show the project-scope reinstall running from its projectPath"
    for foreign in FOREIGN_COMMANDS:
        if foreign in result.stdout:
            return f"dry run plan touches a non-Ailly plugin or package: `{foreign}`"
    calls = box.calls()
    if mutating_calls(calls):
        changed = " ".join([mutating_calls(calls)[0]["bin"]] + mutating_calls(calls)[0]["argv"])
        return f"dry run changed configuration: `{changed}`"
    for harness in ("claude", "codex", "pi"):
        if not any(c["bin"] == harness for c in calls):
            return f"dry run never read {harness} state"

    box.use(MIGRATED)
    result = box.run([sys.executable, str(SCRIPT)])
    if result.returncode != 0:
        return f"dry run on a migrated install exited {result.returncode}"
    for removal in ("claude plugin marketplace remove", "codex plugin marketplace remove", "pi remove"):
        if removal in result.stdout:
            return f"dry run on a migrated install still plans `{removal}`"
    return None


def check_apply(box: Sandbox) -> Optional[str]:
    box.use(LEGACY)
    result = box.run([sys.executable, str(SCRIPT), "--apply"])
    if result.returncode != 0:
        return f"--apply exited {result.returncode}: {(result.stderr or result.stdout).strip()[:160]}"
    calls = mutating_calls(box.calls())
    ran = [" ".join([c["bin"]] + c["argv"]) for c in calls]
    expected = CLAUDE_PLAN + CODEX_PLAN + PI_PLAN
    if sorted(ran) != sorted(expected):
        extra = sorted(set(ran) - set(expected))
        missing = sorted(set(expected) - set(ran))
        return f"--apply ran the wrong commands; missing {missing[:2]}, unexpected {extra[:2]}"
    reason = check_plan_order(ran, "--apply")
    if reason:
        return reason
    research = calls[ran.index(CLAUDE_PLAN[5])]
    if Path(research["cwd"]).resolve() != box.project.resolve():
        return "--apply must run the project-scope reinstall from its projectPath"
    return None


def frontmatter_description(path: Path) -> tuple[str, str]:
    text = read(path)
    parts = text.split("---", 2)
    if not text.startswith("---") or len(parts) < 3:
        return "", ""
    match = re.search(r"(?m)^description:\s*(.*)$", parts[1])
    return parts[1], match.group(1) if match else ""


def check_descriptions() -> Optional[str]:
    for path in DESCRIBED_SKILLS:
        fm, description = frontmatter_description(path)
        where = path.relative_to(REPO)
        if SUCCESSOR not in description or "migrate-to-ailly" not in description:
            return f"{where} description must name {SUCCESSOR} and the migrate-to-ailly script"
        if len(fm) > 1024:
            return f"{where} frontmatter is {len(fm)} chars, over the 1024 cap"
    return None


def manifest_versions(plugin: str) -> list[tuple[str, Optional[str]]]:
    versions = []
    for manifest_dir in (".claude-plugin", ".codex-plugin"):
        path = REPO / plugin / manifest_dir / "plugin.json"
        if path.is_file():
            versions.append((str(path.relative_to(REPO)), json.loads(read(path)).get("version")))
    marketplace = json.loads(read(REPO / ".claude-plugin" / "marketplace.json"))
    entry = next((p for p in marketplace.get("plugins", []) if p.get("name") == plugin), {})
    versions.append((f".claude-plugin/marketplace.json#{plugin}", entry.get("version")))
    return versions


def check_versions() -> Optional[str]:
    expected = {plugin: FINAL_VERSION for plugin in NOTICE_PLUGINS} | UNCHANGED_VERSIONS
    for plugin, version in expected.items():
        for where, actual in manifest_versions(plugin):
            if actual != version:
                return f"{where} version is {actual}, expected {version}"
    return None


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        box = Sandbox(Path(tmp))
        for check in (check_hook, check_dry_run, check_apply):
            reason = check(box)
            if reason:
                return fail(f"repo-moved: {reason}")
    for check in (check_descriptions, check_versions):
        reason = check()
        if reason:
            return fail(f"repo-moved: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
