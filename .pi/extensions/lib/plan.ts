/**
 * Minimal plan.md parsing: `plan.md`'s format (references/phases/plan.md) is
 * a `- [ ] Step N: <name>` checklist; counting steps deterministically tells
 * a driver how many red-green-refactor dispatches to run.
 */

const STEP_LINE = /^-\s*\[[ xX]\]\s*Step\s+(\d+)\s*:/;

export function countPlanSteps(planMarkdown: string): number {
	let max = -1;
	for (const line of planMarkdown.split("\n")) {
		const match = STEP_LINE.exec(line.trim());
		if (match) max = Math.max(max, Number(match[1]));
	}
	return max + 1; // steps are 0-indexed (Step 0: API surface area)
}

/**
 * Build-step completion is verified by a sentinel line the dispatch
 * instructions (lib/prompts/quick-loop-step.md) ask the subagent to append
 * to plan.md — "STEP <n> COMPLETE" or "STEP <n> ABORTED: <reason>" — not by
 * trusting its return text.
 */
export type StepSentinel = { status: "complete" } | { status: "aborted"; reason: string } | { status: "missing" };

export function findStepSentinel(planMarkdown: string, step: number): StepSentinel {
	const completeRe = new RegExp(`^STEP ${step} COMPLETE\\s*$`, "m");
	const abortedRe = new RegExp(`^STEP ${step} ABORTED:\\s*(.*)$`, "m");
	const aborted = abortedRe.exec(planMarkdown);
	if (aborted) return { status: "aborted", reason: aborted[1]?.trim() || "(no reason given)" };
	if (completeRe.test(planMarkdown)) return { status: "complete" };
	return { status: "missing" };
}
