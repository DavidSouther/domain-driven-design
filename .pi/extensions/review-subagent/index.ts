/**
 * Review Workflow
 *
 * Models `general:review`'s Journey (Compose → Dispatch → Converge → Fix →
 * Re-evaluate) as a dedicated pi tool for its two steps that are pure
 * mechanics, not judgment. The Dispatch+Converge implementation lives in
 * `../lib/review.ts` so `ailly_quick_loop` and the long-loop driver can run
 * the exact same contract automatically after every artifact-producing
 * phase, not only when the top-level model remembers to call this tool.
 *
 * Composition (step 1: which specialists apply) stays a judgment call for
 * the calling model, since it requires reading the artifact and matching it
 * against installed specialists' descriptions — genuine selection, not
 * mechanical process. Fix (step 4) and re-evaluate (step 5) likewise stay
 * separate turns/agents per the skill's own "evaluation never emits edits"
 * rule; this tool only ever evaluates.
 */

import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { runReview } from "../lib/review.ts";

const EXTENSION_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(EXTENSION_DIR, "..", "..", "..");

const ReviewRunParams = Type.Object({
	artifactPath: Type.String({ description: "Path (relative to cwd or absolute) to the artifact under review." }),
	specialists: Type.Optional(
		Type.Array(Type.String(), {
			description:
				'Specialist skills to compose in alongside the always-present base reviewer, named the way pi knows them (frontmatter `name`, e.g. "clean-comments-review", "using-domain"). Resolved by searching the current project\'s own .pi/skills or .agents/skills first, then this package\'s skills, then user-global skills — the same precedence pi itself uses — so a newly installed or project-authored specialist works with no change here. A legacy "<plugin>:<skill>" form is also accepted; only the part after the colon is used. Choosing which specialists apply is your call; dispatch and convergence are handled by this tool.',
		}),
	),
	model: Type.Optional(Type.String({ description: "Model id/pattern every reviewer and the convergence step run with." })),
});

export default function (pi: ExtensionAPI) {
	pi.registerTool({
		name: "review_run",
		label: "Review Run",
		description: [
			"Run general:review's Dispatch and Converge steps as a single tool call:",
			"the base four-criterion reviewer plus any named specialists run in",
			"parallel, isolated subprocesses, then a dedicated convergence",
			"subprocess verifies, deduplicates, and severity-ranks their findings.",
			"Returns the converged, ranked list — never a flat unverified dump.",
			"Composition (which specialists apply), fixing, and re-evaluation stay",
			"separate steps for you to run after this call.",
		].join(" "),
		parameters: ReviewRunParams,

		async execute(_toolCallId, params, signal, onUpdate, ctx) {
			const result = await runReview({
				artifactPath: params.artifactPath,
				specialists: params.specialists,
				model: params.model,
				cwd: ctx.cwd,
				repoRoot: REPO_ROOT,
				signal,
				onProgress: (text) => onUpdate?.({ content: [{ type: "text", text: `Reviewing ${params.artifactPath}...\n\n${text}` }] }),
			});

			if ("error" in result) {
				return {
					content: [{ type: "text", text: result.error }],
					isError: true,
					details: { artifactPath: params.artifactPath },
				};
			}

			const header = `Review of ${params.artifactPath} — ${result.reviewerOutcomes.length} reviewer(s) composed, converged findings below`;
			const body = result.convergenceFailed
				? `Convergence FAILED: ${result.convergence.errorMessage || result.convergence.stderr || "(no output)"}`
				: result.convergence.output || "(no output)";

			return {
				content: [{ type: "text", text: `${header}\n\n${body}` }],
				isError: result.anyReviewerFailed || result.convergenceFailed,
				details: result,
			};
		},
	});
}
