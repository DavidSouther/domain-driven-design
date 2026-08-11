/**
 * Minimal plan.md parsing shared by the quick-loop and long-loop drivers.
 *
 * `plan.md`'s own format (developer/skills/ailly/references/phases/plan.md)
 * is a `- [ ] Step N: <name>` checklist. Counting those steps deterministically
 * is what lets a driver know how many red-green-refactor dispatches to run
 * without asking a model to "remember" the plan's shape.
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
 * Build-step completion is verified by a sentinel line the quick-loop/
 * long-loop dispatch instructions ask the red-green-refactor subagent to
 * append to plan.md, not by trusting the subagent's own return text:
 * "STEP <n> COMPLETE" or "STEP <n> ABORTED: <reason>".
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
