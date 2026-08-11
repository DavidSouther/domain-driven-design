/**
 * Shared Ailly phase/ability reference dispatch.
 *
 * Factored out of `ailly_subagent` so `ailly_quick_loop` and the long-loop
 * driver can dispatch the same isolated-reference contract without going
 * through the tool-calling LLM in between phases.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { runPiSubprocess, type SubprocessRunResult } from "./subprocess.ts";

/**
 * Canonical reference names Ailly dispatches by. Each maps to a file
 * resolved relative to a package root passed in by the caller, not the
 * caller's cwd, so the mapping holds regardless of where this package ends
 * up installed.
 */
export const PHASE_REFERENCES: Record<string, string> = {
	research: "developer/skills/ailly/references/phases/research.md",
	design: "developer/skills/ailly/references/phases/design.md",
	plan: "developer/skills/ailly/references/phases/plan.md",
	"red-green-refactor": "developer/skills/ailly/references/phases/red-green-refactor.md",
	build: "developer/skills/ailly/references/phases/red-green-refactor.md",
	cleanup: "developer/skills/ailly/references/phases/cleanup.md",
	thinking: "developer/skills/ailly/references/abilities/thinking.md",
	refactor: "developer/skills/ailly/references/abilities/refactor.md",
	initialize: "developer/skills/ailly/references/abilities/initialize.md",
	"intent-review": "developer/skills/ailly/references/abilities/intent-review.md",
};

export interface RunAillyReferenceResult {
	reference: string;
	referencePath: string;
	error?: string;
	run?: SubprocessRunResult;
}

export interface RunAillyReferenceOptions {
	reference: string;
	task: string;
	model?: string;
	cwd: string;
	repoRoot: string;
	signal?: AbortSignal;
	/** Rolling recent-activity lines from the dispatched subprocess, for live progress display. */
	onProgress?: (recentLines: string[]) => void;
}

/** Dispatch exactly one Ailly phase/ability reference as an isolated pi subprocess. */
export async function runAillyReference(opts: RunAillyReferenceOptions): Promise<RunAillyReferenceResult> {
	const { reference, task, model, cwd, repoRoot, signal, onProgress } = opts;
	const relPath = PHASE_REFERENCES[reference];
	if (!relPath) {
		return { reference, referencePath: "", error: `Unknown reference: "${reference}"` };
	}
	const absPath = path.join(repoRoot, relPath);
	let referenceBody: string;
	try {
		referenceBody = await fs.promises.readFile(absPath, "utf-8");
	} catch (err) {
		return { reference, referencePath: relPath, error: `Could not read reference ${relPath}: ${(err as Error).message}` };
	}

	const systemPrompt = [
		"You are an isolated Ailly phase/ability subagent, dispatched by developer:ailly.",
		`Read only the reference below (sourced from ${relPath}) and execute it exactly.`,
		"Do not read any other developer:ailly phase or ability reference in this process.",
		"",
		referenceBody,
	].join("\n");

	const run = await runPiSubprocess({ label: reference, systemPrompt, task, model, cwd, signal, onProgress });
	return { reference, referencePath: relPath, run };
}
