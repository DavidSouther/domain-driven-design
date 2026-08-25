/**
 * Ailly File Permissions Mode
 *
 * A pi files-allowed permission mode (see `permission-gate.ts` and
 * `protected-paths.ts` in @earendil-works/pi-coding-agent's own
 * `examples/extensions/` for the base `tool_call` gating pattern this
 * builds on) that dynamically restricts which files can be read, written,
 * edited, or `bash`-deleted based on developer:ailly's *current phase* —
 * detected from the on-disk session folder under `.ailly/developer/` (see
 * developer/skills/ailly/SKILL.md's "Session Folder" table), not a static
 * allowlist config file. Every rule below is lifted from that phase's own
 * reference doc's stated "Hard gate" or "Do not" clause, not invented here.
 *
 * - **Research phase**: `references/phases/research.md` ends with "Do not
 *   write a design or a feature test. Do not enter the design phase." —
 *   reads are unrestricted (research has to survey the whole project), but
 *   writes/edits are confined to `.ailly/` (research.md and its `research/`
 *   notes folder). No source-tree file exists yet by design.
 * - **Design phase**: reads are confined to `research/` (the research:*
 *   skill content the design checklist's "Research additional context"
 *   step permits consulting) and `.ailly/` (the session workspace).
 *   `research/` only resolves to anything in a project that vendors a
 *   top-level `research/` tree the way this package's own repo does —
 *   installed elsewhere, that half of the allowlist is inert and reads
 *   narrow to `.ailly/`. Writes are confined to `.ailly/` plus exactly one
 *   test-file path — `references/phases/design.md`'s "single exception to
 *   the no-code rule" — the one feature test the phase records in
 *   `design.md`; a second, different test-file path is refused so "exactly
 *   one executable feature test" stays true even under this gate.
 * - **Plan phase**: `references/phases/plan.md`'s Hard gate is explicit —
 *   "Do not implement any step. Do not write unit tests or implementation
 *   code" — every code sample in the plan (including Step 0's API stubs)
 *   is markdown *inside* `plan.md`, never a real source file. Writes are
 *   confined to `.ailly/`; reads stay unrestricted (planning has to see the
 *   existing codebase the new steps land in).
 * - **Build phase (red-green-refactor)**: once a test run's outcome is
 *   known, edits are confined to implementation files while the last run
 *   failed ("red"), and to test files while it last passed ("green") — the
 *   inverse of the phase's own vocabulary, because that is what drives the
 *   loop forward: red means "make it pass" (implementation edits), green
 *   means "write the next test" (test edits). Before any test has run this
 *   build phase (writing type-first signatures, then the first test),
 *   nothing is restricted, since there is no outcome yet to gate against.
 * - **Cleanup phase**: `references/phases/cleanup.md` is the only phase
 *   whose job includes "Remove the `.ailly/developer/YYYY-MM-DD-A-<topic>`
 *   folder" — so it is the only phase this mode lets delete anything under
 *   `.ailly/`. Every other phase has a `bash` command blocked if it looks
 *   destructive (`rm`, `git rm`, `find -delete`, a clobbering `>` redirect,
 *   …) and references a `.ailly` path, protecting the session's research,
 *   design, and plan artifacts from being wiped mid-flight. Reads and
 *   writes are otherwise unrestricted in cleanup, matching its own mandate
 *   to run formatters and refactor passes across the whole tree.
 *
 * Known trade-off: `references/abilities/refactor.md`'s post-green
 * implementation cleanup falls inside the "green" window the build-phase
 * rule confines to test-only edits. Drop a `.ailly/.file-mode-override`
 * marker file (any content) to disable every rule in this mode — including
 * the deletion guard — until the marker is removed again.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI, ExtensionContext, ToolCallEvent } from "@earendil-works/pi-coding-agent";
import { isBashToolResult, isToolCallEventType } from "@earendil-works/pi-coding-agent";
import {
	detectPhase,
	findActiveSessionFolder,
	isTestPath,
	isUnderAny,
	looksDestructive,
	looksLikeTestRun,
} from "../lib/ailly-file-mode.ts";

type TestOutcome = "red" | "green";

function overrideActive(cwd: string): boolean {
	return fs.existsSync(path.join(cwd, ".ailly", ".file-mode-override"));
}

/** All five gated tools take a `path` argument (default "." when omitted). */
function targetPath(event: ToolCallEvent): string {
	const input = event.input as { path?: string };
	return input.path ?? ".";
}

function deny(ctx: ExtensionContext, reason: string) {
	if (ctx.hasUI) ctx.ui.notify(reason, "warning");
	return { block: true, reason };
}

export default function (pi: ExtensionAPI) {
	// Last known test-run outcome per session folder, build phase only.
	// Reset per process, so each isolated ailly_subagent dispatch (one
	// build-phase step) starts from "no signal yet" — matching the loop's
	// own scope of one plan step's worth of red/green cycling.
	const lastOutcome = new Map<string, TestOutcome>();

	// The one feature-test path a design phase has committed to, per session
	// folder — enforces design.md's "exactly one executable feature test."
	const designFeatureTest = new Map<string, string>();

	pi.on("tool_result", async (event, ctx) => {
		if (!isBashToolResult(event)) return undefined;
		const command = (event.input as { command?: string }).command;
		if (!command || !looksLikeTestRun(command)) return undefined;

		const sessionFolder = findActiveSessionFolder(ctx.cwd);
		if (!sessionFolder || detectPhase(sessionFolder) !== "build") return undefined;

		lastOutcome.set(sessionFolder, event.isError ? "red" : "green");
		return undefined;
	});

	pi.on("tool_call", async (event, ctx) => {
		if (overrideActive(ctx.cwd)) return undefined;

		if (isToolCallEventType("bash", event)) {
			const command = event.input.command;
			const referencesAilly = command.includes(".ailly") && !command.includes(".file-mode-override");
			if (referencesAilly && looksDestructive(command)) {
				const phase = detectPhase(findActiveSessionFolder(ctx.cwd));
				if (phase !== "cleanup") {
					return deny(
						ctx,
						`Ailly ${phase} phase: only the cleanup phase may delete or clobber .ailly/ session artifacts (blocked command referencing .ailly)`,
					);
				}
			}
			return undefined;
		}

		const isRead =
			isToolCallEventType("read", event) ||
			isToolCallEventType("grep", event) ||
			isToolCallEventType("find", event) ||
			isToolCallEventType("ls", event);
		const isWrite = isToolCallEventType("write", event) || isToolCallEventType("edit", event);
		if (!isRead && !isWrite) return undefined;

		const sessionFolder = findActiveSessionFolder(ctx.cwd);
		const phase = detectPhase(sessionFolder);
		if (phase === "cleanup") return undefined;

		const rawPath = targetPath(event);
		const absPath = path.resolve(ctx.cwd, rawPath);
		const relPath = path.relative(ctx.cwd, absPath);

		if (phase === "research") {
			if (isWrite && !isUnderAny(rawPath, ctx.cwd, [".ailly"])) {
				return deny(ctx, `Ailly research phase: writes are confined to .ailly/ (blocked "${relPath}")`);
			}
			return undefined; // reads unrestricted
		}

		if (phase === "plan") {
			if (isWrite && !isUnderAny(rawPath, ctx.cwd, [".ailly"])) {
				return deny(ctx, `Ailly plan phase: writes are confined to .ailly/ — plan steps are markdown, not code (blocked "${relPath}")`);
			}
			return undefined; // reads unrestricted
		}

		if (phase === "design") {
			if (isWrite) {
				if (isUnderAny(rawPath, ctx.cwd, [".ailly"])) return undefined;
				if (!isTestPath(relPath)) {
					return deny(ctx, `Ailly design phase: writes are confined to .ailly/ or the one feature test file (blocked "${relPath}")`);
				}
				if (sessionFolder) {
					const committed = designFeatureTest.get(sessionFolder);
					if (committed && committed !== absPath) {
						return deny(
							ctx,
							`Ailly design phase: only one feature test file per design (already using "${path.relative(ctx.cwd, committed)}", blocked "${relPath}")`,
						);
					}
					designFeatureTest.set(sessionFolder, absPath);
				}
				return undefined;
			}
			if (!isUnderAny(rawPath, ctx.cwd, ["research", ".ailly"])) {
				return deny(ctx, `Ailly design phase: reads are confined to research/ and .ailly/ (blocked "${relPath}")`);
			}
			return undefined;
		}

		// phase === "build": reads are unrestricted; edits gate on the last known test outcome.
		if (!isWrite || !sessionFolder) return undefined;
		const outcome = lastOutcome.get(sessionFolder);
		if (!outcome) return undefined; // no test has run yet this build phase — nothing to gate against

		const editingTest = isTestPath(relPath);
		if (outcome === "red" && editingTest) {
			return deny(
				ctx,
				`Ailly build phase (red): only implementation edits are allowed until the failing test passes (blocked test file "${relPath}")`,
			);
		}
		if (outcome === "green" && !editingTest) {
			return deny(
				ctx,
				`Ailly build phase (green): only test edits are allowed while tests pass (blocked implementation file "${relPath}"). Drop .ailly/.file-mode-override to refactor.`,
			);
		}
		return undefined;
	});
}
