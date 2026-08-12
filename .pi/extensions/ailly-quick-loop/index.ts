/**
 * ailly_quick_loop: developer:ailly's Quick-loop Mode as one deterministic
 * driver — research → design → plan (each reviewed) → red-green-refactor per
 * plan step (verified via a plan.md sentinel, not self-report) → diff review.
 * Stops at the first missing artifact or aborted step; pauses before Cleanup
 * unless `noReview` is set.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { runAillyReference } from "../lib/ailly-phases.ts";
import { loadPrompt } from "../lib/prompts.ts";
import { countPlanSteps, findStepSentinel } from "../lib/plan.ts";
import { runReview } from "../lib/review.ts";
import { isFailed, nextDatedSlug, slugify, todayIso } from "../lib/subprocess.ts";

const EXTENSION_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(EXTENSION_DIR, "..", "..", "..");

const ReviewSpecialistsSchema = Type.Object(
	{
		research: Type.Optional(Type.Array(Type.String())),
		design: Type.Optional(Type.Array(Type.String())),
		plan: Type.Optional(Type.Array(Type.String())),
		build: Type.Optional(Type.Array(Type.String())),
	},
	{ description: "Specialist skill names (per review_run's naming rules) to compose in for each phase's artifact review." },
);

const QuickLoopParams = Type.Object({
	topic: Type.String({ description: "Short topic/feature description, used for the session folder slug and phase context." }),
	sessionFolder: Type.Optional(
		Type.String({ description: "Resume an existing session folder instead of creating a new one." }),
	),
	noReview: Type.Optional(
		Type.Boolean({
			description:
				"Skip the post-green human review pause and run Cleanup immediately, per quick-loop's 'no review' escape hatch. Default: false (pause before Cleanup).",
		}),
	),
	reviewSpecialists: Type.Optional(ReviewSpecialistsSchema),
	model: Type.Optional(Type.String({ description: "Model id/pattern every phase dispatch and review runs with." })),
});

interface PhaseOutcome {
	phase: string;
	dispatchError?: string;
	dispatchOutput?: string;
	artifactFound: boolean;
	review?: { converged: string; failed: boolean };
	halted?: string;
}

export default function (pi: ExtensionAPI) {
	pi.registerTool({
		name: "ailly_quick_loop",
		label: "Ailly Quick Loop",
		description: [
			"Run developer:ailly's quick-loop mode end to end in one call: research,",
			"design, plan, then red-green-refactor once per plan step (verified via a",
			"sentinel line appended to plan.md, not self-report), reviewing every",
			"artifact with review_run's Dispatch+Converge as it goes. Stops and",
			"reports at the first missing artifact or aborted build step rather than",
			"plowing through. Pauses before Cleanup unless noReview is set. Use for",
			"small, unambiguous, narrow-surface tasks — the same fit quick-loop's own",
			"guidance names; prefer ailly_subagent phase-by-phase, or ailly_long_loop_start,",
			"for ambiguous or high-blast-radius work.",
		].join(" "),
		parameters: QuickLoopParams,

		async execute(_toolCallId, params, signal, onUpdate, ctx) {
			const cwd = ctx.cwd;
			const model = params.model;
			const sessionFolder = await resolveAillySessionFolder(cwd, params.topic, params.sessionFolder);
			const outcomes: PhaseOutcome[] = [];
			const report = (line: string) => onUpdate?.({ content: [{ type: "text", text: line }] });

			report(`Session folder: ${sessionFolder}`);

			let startSha: string | null = null;
			try {
				const rev = await pi.exec("git", ["rev-parse", "HEAD"], { cwd });
				if (rev.code === 0) startSha = rev.stdout.trim();
			} catch {
				startSha = null;
			}

			const docPhases: Array<{ phase: string; file: string }> = [
				{ phase: "research", file: "research.md" },
				{ phase: "design", file: "design.md" },
				{ phase: "plan", file: "plan.md" },
			];

			for (const { phase, file } of docPhases) {
				report(`Dispatching ${phase}...`);
				const dispatch = await runAillyReference({
					reference: phase,
					task: loadPrompt("quick-loop-phase", { topic: params.topic, sessionFolder }),
					model,
					cwd,
					repoRoot: REPO_ROOT,
					signal,
					onProgress: (lines) => report(`Dispatching ${phase}...\n\n${lines.join("\n")}`),
				});

				const artifactPath = path.join(sessionFolder, file);
				const artifactFound = fs.existsSync(artifactPath);
				const outcome: PhaseOutcome = { phase, artifactFound, dispatchOutput: dispatch.run?.output };
				if (dispatch.error || !dispatch.run || isFailed(dispatch.run)) {
					outcome.dispatchError = dispatch.error ?? dispatch.run?.errorMessage ?? dispatch.run?.stderr ?? "dispatch failed";
				}
				if (!artifactFound) {
					outcome.halted = `${phase} did not produce ${file}; halting quick loop`;
					outcomes.push(outcome);
					return finish(outcomes, sessionFolder, false, false);
				}

				report(`Reviewing ${file}...`);
				const specialists = (params.reviewSpecialists as Record<string, string[] | undefined> | undefined)?.[phase];
				const review = await runReview({
					artifactPath,
					specialists,
					model,
					cwd,
					repoRoot: REPO_ROOT,
					signal,
					onProgress: (text) => report(`Reviewing ${file}...\n\n${text}`),
				});
				outcome.review = "error" in review
					? { converged: review.error, failed: true }
					: { converged: review.convergence.output || "(no output)", failed: review.anyReviewerFailed || review.convergenceFailed };
				outcomes.push(outcome);
			}

			// Build loop: one red-green-refactor dispatch per plan step, verified via sentinel.
			const planPath = path.join(sessionFolder, "plan.md");
			const planContentAtStart = await fs.promises.readFile(planPath, "utf-8");
			const stepCount = countPlanSteps(planContentAtStart);
			if (stepCount <= 0) {
				outcomes.push({ phase: "build", artifactFound: false, halted: "plan.md has no recognizable steps; halting quick loop" });
				return finish(outcomes, sessionFolder, false, false);
			}

			let buildHalted = false;
			for (let step = 0; step < stepCount; step++) {
				report(`Dispatching red-green-refactor for step ${step}/${stepCount - 1}...`);
				const buildDispatch = await runAillyReference({
					reference: "red-green-refactor",
					task: loadPrompt("quick-loop-step", { step: String(step), planPath, sessionFolder }),
					model,
					cwd,
					repoRoot: REPO_ROOT,
					signal,
					onProgress: (lines) => report(`Dispatching red-green-refactor for step ${step}/${stepCount - 1}...\n\n${lines.join("\n")}`),
				});

				const planContentNow = await fs.promises.readFile(planPath, "utf-8");
				const sentinel = findStepSentinel(planContentNow, step);
				const outcome: PhaseOutcome = { phase: `build-step-${step}`, artifactFound: true, dispatchOutput: buildDispatch.run?.output };
				if (sentinel.status === "aborted") {
					outcome.halted = `Step ${step} aborted: ${sentinel.reason}`;
					outcomes.push(outcome);
					buildHalted = true;
					break;
				}
				if (sentinel.status === "missing") {
					outcome.halted = `Step ${step} did not append its completion sentinel to plan.md; treating as a broken contract and halting`;
					outcomes.push(outcome);
					buildHalted = true;
					break;
				}
				outcomes.push(outcome);
			}

			if (buildHalted) return finish(outcomes, sessionFolder, false, false);

			// Review the accumulated diff, if any.
			if (startSha) {
				try {
					const diff = await pi.exec("git", ["diff", startSha], { cwd });
					if (diff.code === 0 && diff.stdout.trim()) {
						const diffPath = path.join(sessionFolder, "build.diff");
						await fs.promises.writeFile(diffPath, diff.stdout, "utf-8");
						report("Reviewing build.diff...");
						const review = await runReview({
							artifactPath: diffPath,
							specialists: params.reviewSpecialists?.build,
							model,
							cwd,
							repoRoot: REPO_ROOT,
							signal,
							onProgress: (text) => report(`Reviewing build.diff...\n\n${text}`),
						});
						outcomes.push({
							phase: "build",
							artifactFound: true,
							review:
								"error" in review
									? { converged: review.error, failed: true }
									: { converged: review.convergence.output || "(no output)", failed: review.anyReviewerFailed || review.convergenceFailed },
						});
					}
				} catch {
					// No git, or nothing to diff — not a halt condition.
				}
			}

			if (params.noReview) {
				report("Dispatching cleanup...");
				const cleanup = await runAillyReference({
					reference: "cleanup",
					task: `Session folder: ${sessionFolder}. Quick-loop 'no review' mode: proceed directly to cleanup.`,
					model,
					cwd,
					repoRoot: REPO_ROOT,
					signal,
					onProgress: (lines) => report(`Dispatching cleanup...\n\n${lines.join("\n")}`),
				});
				outcomes.push({
					phase: "cleanup",
					artifactFound: true,
					dispatchError: cleanup.error ?? (cleanup.run && isFailed(cleanup.run) ? cleanup.run.errorMessage || cleanup.run.stderr : undefined),
				});
				return finish(outcomes, sessionFolder, true, true);
			}

			return finish(outcomes, sessionFolder, true, false);
		},
	});
}

function finish(outcomes: PhaseOutcome[], sessionFolder: string, buildGreen: boolean, cleanedUp: boolean) {
	const lines = outcomes.map((o) => {
		const parts = [`## ${o.phase}`];
		if (o.dispatchError) parts.push(`Dispatch error: ${o.dispatchError}`);
		if (o.halted) {
			parts.push(`HALTED: ${o.halted}`);
			if (o.dispatchOutput) parts.push(`Dispatch's own output (for diagnosis):\n${o.dispatchOutput}`);
		}
		if (o.review) parts.push(`Review (${o.review.failed ? "FAILED" : "ok"}):\n${o.review.converged}`);
		return parts.join("\n");
	});
	const halted = outcomes.some((o) => o.halted);
	const status = halted
		? "HALTED — see the phase above for why."
		: cleanedUp
			? "Complete: cleanup ran (noReview mode)."
			: "Green and reviewed. Paused before Cleanup — review the session artifacts, then ask to proceed and run cleanup (ailly_subagent with reference: \"cleanup\").";

	return {
		content: [{ type: "text", text: `Quick loop — session ${sessionFolder}\nStatus: ${status}\n\n${lines.join("\n\n")}` }],
		isError: halted,
		details: { sessionFolder, outcomes, buildGreen, cleanedUp },
	};
}
