/**
 * ailly-file-permissions: a `tool_call` gate (see `protected-paths.ts` and
 * `permission-gate.ts` in @earendil-works/pi-coding-agent's own
 * `examples/extensions/`) that confines read/write/edit/destructive-bash
 * calls to whatever developer:ailly's *current phase* allows. Each phase's
 * rule is sourced from that phase's own reference doc's stated "Hard gate"
 * — see developer/skills/ailly/references/agents/pi.md's "File Permissions
 * Mode" section for the full per-phase breakdown; don't re-derive it here.
 *
 * The phase is re-detected from the on-disk session folder on every call,
 * never cached, so a draft cleared mid-session takes effect immediately.
 *
 * Drop a `.ailly/.file-mode-override` marker file (any content) to disable
 * every rule below, including the deletion guard — needed because the
 * build phase's "green" rule blocks `references/abilities/refactor.md`'s
 * own implementation edits.
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
