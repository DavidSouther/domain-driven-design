/**
 * Ailly File Permissions Mode
 *
 * A pi files-allowed permission mode (see `permission-gate.ts` and
 * `protected-paths.ts` in @earendil-works/pi-coding-agent's own
 * `examples/extensions/` for the base `tool_call` gating pattern this
 * builds on) that dynamically restricts which files can be read, written,
 * or edited based on developer:ailly's *current phase* — detected from the
 * on-disk session folder under `.ailly/developer/` (see
 * developer/skills/ailly/SKILL.md's "Session Folder" table), not a static
 * allowlist config file.
 *
 * - **Design phase**: reads are confined to `research/` (the research:*
 *   skill content the design checklist's "Research additional context"
 *   step permits consulting) and `.ailly/` (the session workspace);
 *   writes/edits are confined to `.ailly/` only. `research/` only resolves
 *   to anything in a project that vendors a top-level `research/` tree the
 *   way this package's own repo does — installed elsewhere, that half of
 *   the allowlist is simply inert and reads narrow to `.ailly/`.
 * - **Build phase (red-green-refactor)**: once a test run's outcome is
 *   known, edits are confined to implementation files while the last run
 *   failed ("red"), and to test files while it last passed ("green") — the
 *   inverse of the phase's own vocabulary, because that is what drives the
 *   loop forward: red means "make it pass" (implementation edits), green
 *   means "write the next test" (test edits). Before any test has run this
 *   build phase (writing type-first signatures, then the first test),
 *   nothing is restricted, since there is no outcome yet to gate against.
 * - **Research, plan, and cleanup phases** are unrestricted.
 *
 * Known trade-off: `references/abilities/refactor.md`'s post-green
 * implementation cleanup falls inside the "green" window this mode
 * confines to test-only edits. Drop a `.ailly/.file-mode-override` marker
 * file (any content) next to the session folders to disable this mode's
 * gating until the marker is removed again.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI, ExtensionContext, ToolCallEvent } from "@earendil-works/pi-coding-agent";
import { isBashToolResult, isToolCallEventType } from "@earendil-works/pi-coding-agent";
import { detectPhase, findActiveSessionFolder, isTestPath, isUnderAny, looksLikeTestRun } from "../lib/ailly-file-mode.ts";

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
		const isRead = isToolCallEventType("read", event) || isToolCallEventType("grep", event) || isToolCallEventType("find", event) || isToolCallEventType("ls", event);
		const isWrite = isToolCallEventType("write", event) || isToolCallEventType("edit", event);
		if (!isRead && !isWrite) return undefined;
		if (overrideActive(ctx.cwd)) return undefined;

		const sessionFolder = findActiveSessionFolder(ctx.cwd);
		const phase = detectPhase(sessionFolder);
		if (phase === "research" || phase === "plan" || phase === "cleanup") return undefined;

		const rawPath = targetPath(event);
		const relPath = path.relative(ctx.cwd, path.resolve(ctx.cwd, rawPath));

		if (phase === "design") {
			if (isWrite) {
				if (!isUnderAny(rawPath, ctx.cwd, [".ailly"])) {
					return deny(ctx, `Ailly design phase: writes are confined to .ailly/ (blocked "${relPath}")`);
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
