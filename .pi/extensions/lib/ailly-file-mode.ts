/**
 * Shared phase detection and path-matching helpers for the
 * `ailly-file-permissions` extension.
 *
 * Phase is read straight off disk — the same signal developer:ailly's own
 * Resume table uses (developer/skills/ailly/SKILL.md's "Session Folder"
 * section: which of research.md/design.md/plan.md exist under the active
 * `.ailly/developer/<session>/` folder, and whether each has cleared its
 * `*Draft*` marker) — rather than a separate state file this extension
 * would have to keep in sync itself.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { countPlanSteps, findStepSentinel } from "./plan.ts";
import { listAillySessionDirs } from "./session.ts";

export type AillyPhase = "research" | "design" | "plan" | "build" | "cleanup";

const DRAFT_MARKER = /\*Draft\b/i;

function isDraftCleared(filePath: string): boolean {
	let text: string;
	try {
		text = fs.readFileSync(filePath, "utf-8");
	} catch {
		return false;
	}
	return !DRAFT_MARKER.test(text);
}

/** Latest mtime (ms) of `entryPath` or, recursively, anything under it. */
function latestMtimeMs(entryPath: string): number {
	let stat: fs.Stats;
	try {
		stat = fs.statSync(entryPath);
	} catch {
		return -Infinity;
	}
	if (!stat.isDirectory()) return stat.mtimeMs;
	let latest = stat.mtimeMs;
	for (const child of fs.readdirSync(entryPath)) {
		latest = Math.max(latest, latestMtimeMs(path.join(entryPath, child)));
	}
	return latest;
}

/**
 * The most recently touched `.ailly/developer/*` session folder under `cwd`,
 * or null if no Ailly session has been started yet. Ailly runs one session
 * at a time in practice, but when several topics' folders exist, the most
 * recently modified one is the active one.
 */
export function findActiveSessionFolder(cwd: string): string | null {
	const dirs = listAillySessionDirs(cwd);
	if (dirs.length === 0) return null;
	return dirs.reduce((latest, dir) => (latestMtimeMs(dir) > latestMtimeMs(latest) ? dir : latest));
}

/**
 * Determine the current Ailly phase from a session folder's artifacts,
 * mirroring the Resume table in developer/skills/ailly/SKILL.md's "Session
 * Folder" section. `null` (no session folder yet) reads as "research", the
 * phase a brand new session starts at.
 */
export function detectPhase(sessionFolder: string | null): AillyPhase {
	if (!sessionFolder) return "research";

	const researchPath = path.join(sessionFolder, "research.md");
	const designPath = path.join(sessionFolder, "design.md");
	const planPath = path.join(sessionFolder, "plan.md");

	if (fs.existsSync(planPath)) {
		if (!isDraftCleared(planPath)) return "plan";

		let planMarkdown: string;
		try {
			planMarkdown = fs.readFileSync(planPath, "utf-8");
		} catch {
			return "build";
		}
		const stepCount = countPlanSteps(planMarkdown);
		const allStepsComplete =
			stepCount > 0 &&
			Array.from({ length: stepCount }, (_, step) => step).every(
				(step) => findStepSentinel(planMarkdown, step).status === "complete",
			);
		return allStepsComplete ? "cleanup" : "build";
	}

	if (fs.existsSync(designPath)) {
		return isDraftCleared(designPath) ? "plan" : "design";
	}

	if (fs.existsSync(researchPath)) {
		return isDraftCleared(researchPath) ? "design" : "research";
	}

	return "research";
}

/** True when `targetPath` (relative or absolute) resolves inside one of `roots` (relative to `cwd`). */
export function isUnderAny(targetPath: string, cwd: string, roots: string[]): boolean {
	const absTarget = path.resolve(cwd, targetPath);
	return roots.some((root) => {
		const absRoot = path.resolve(cwd, root);
		const rel = path.relative(absRoot, absTarget);
		return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
	});
}

// Common test-file naming conventions across languages, matched against a
// path relative to cwd. Deliberately broad (false positives just mean a
// non-test file is treated as a test during the build phase's gate, which
// only narrows *where* an edit lands, never blocks a read).
const TEST_PATH_PATTERNS: RegExp[] = [
	/(^|[/\\])(tests?|specs?|__tests__|__specs__)[/\\]/i,
	/\.(test|spec)\.[^./\\]+$/i,
	/(^|[/\\])test_[^/\\]+\.[^./\\]+$/i,
	/_test\.[^./\\]+$/i,
	/_spec\.[^./\\]+$/i,
	/\.feature$/i,
];

export function isTestPath(relPath: string): boolean {
	return TEST_PATH_PATTERNS.some((re) => re.test(relPath));
}

// Common test-runner invocations, matched against a bash command string.
const TEST_RUN_COMMAND_PATTERNS: RegExp[] = [
	/\b(npm|pnpm|yarn|bun)\s+(run\s+)?test\b/i,
	/\bpytest\b/i,
	/\bpython[0-9.]*\s+-m\s+pytest\b/i,
	/\bgo\s+test\b/i,
	/\bcargo\s+test\b/i,
	/\b(mvn|gradle|\.\/gradlew)\b.*\btest\b/i,
	/\b(rspec|bundle\s+exec\s+rspec)\b/i,
	/\b(jest|vitest|mocha|ava)\b/i,
	/\bdotnet\s+test\b/i,
	/\bctest\b/i,
	/\btox\b/i,
	/\bmake\s+test\b/i,
];

export function looksLikeTestRun(command: string): boolean {
	return TEST_RUN_COMMAND_PATTERNS.some((re) => re.test(command));
}
