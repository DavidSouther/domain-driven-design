/**
 * Review Workflow
 *
 * Models `general:review`'s Journey (Compose → Dispatch → Converge → Fix →
 * Re-evaluate) as a dedicated pi tool for its two steps that are pure
 * mechanics, not judgment:
 *
 * - **Dispatch (step 2).** Every composed reviewer — the always-present base
 *   four-criterion reviewer plus any specialists — runs in its own isolated
 *   subprocess, in parallel, so lenses cannot cross-contaminate.
 * - **Converge (step 3, "mandatory").** The skill is explicit that a flat,
 *   unverified dump must never reach the fix pass. This tool always runs a
 *   dedicated convergence subprocess — verify against the artifact,
 *   deduplicate, severity-rank — so that step cannot be silently skipped by
 *   an orchestrating model in a hurry.
 *
 * Composition (step 1: which specialists apply) stays a judgment call for
 * the calling model, since it requires reading the artifact and matching it
 * against installed specialists' descriptions — genuine selection, not
 * mechanical process. Fix (step 4) and re-evaluate (step 5) likewise stay
 * separate turns/agents per the skill's own "evaluation never emits edits"
 * rule; this tool only ever evaluates.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { findSkillByName, specialistSkillName } from "../lib/skills.ts";
import { isFailed, runPiSubprocess } from "../lib/subprocess.ts";

const EXTENSION_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(EXTENSION_DIR, "..", "..", "..");
const REVIEW_SKILL_PATH = "general/skills/review/SKILL.md";

function extractSection(markdown: string, heading: string): string {
	const lines = markdown.split("\n");
	const startIndex = lines.findIndex((line) => line.trim() === `## ${heading}`);
	if (startIndex === -1) return "";
	const rest = lines.slice(startIndex + 1);
	const endOffset = rest.findIndex((line) => /^##\s+/.test(line));
	const body = endOffset === -1 ? rest : rest.slice(0, endOffset);
	return body.join("\n").trim();
}

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

		async execute(_toolCallId, params, signal, _onUpdate, ctx) {
			const artifactAbsPath = path.resolve(ctx.cwd, params.artifactPath);
			let artifactContent: string;
			try {
				artifactContent = await fs.promises.readFile(artifactAbsPath, "utf-8");
			} catch (err) {
				return {
					content: [{ type: "text", text: `Could not read artifact ${params.artifactPath}: ${(err as Error).message}` }],
					isError: true,
					details: { artifactPath: params.artifactPath },
				};
			}

			const reviewSkillText = await fs.promises.readFile(path.join(REPO_ROOT, REVIEW_SKILL_PATH), "utf-8");
			const baseRubric = extractSection(reviewSkillText, "Base Reviewer");

			type ReviewerJob = { id: string; skillPath: string | null; systemPrompt: string | null; error?: string };

			const jobs: ReviewerJob[] = [
				{
					id: "base",
					skillPath: path.join(REPO_ROOT, REVIEW_SKILL_PATH),
					systemPrompt: [
						"You are the always-present base reviewer from general:review's composed set.",
						"Evaluate the artifact below against exactly these four criteria. Do not fix",
						"anything. List verified findings ranked by severity (High/Medium/Low).",
						"",
						baseRubric,
						"",
						`## Artifact (${params.artifactPath})`,
						"",
						artifactContent,
					].join("\n"),
				},
				...(params.specialists ?? []).map((specialist): ReviewerJob => {
					const name = specialistSkillName(specialist);
					const absPath = findSkillByName(name, REPO_ROOT, ctx.cwd);
					if (!absPath) {
						return {
							id: specialist,
							skillPath: null,
							systemPrompt: null,
							error: `No loaded skill named "${name}" found in the project's .pi/skills or .agents/skills, this package's skills, or user-global skills`,
						};
					}
					return { id: specialist, skillPath: absPath, systemPrompt: null };
				}),
			];

			for (const job of jobs) {
				if (job.error) continue;
				try {
					const body = await fs.promises.readFile(job.skillPath!, "utf-8");
					job.systemPrompt =
						job.id === "base"
							? job.systemPrompt
							: [
									`You are the specialist reviewer "${job.id}", composed into general:review's set because its`,
									"description matched this artifact. Produce your own critique per your skill",
									"below against the artifact. Your critique document is your findings — do not",
									"write a generic rubric first. Do not fix anything.",
									"",
									body,
									"",
									`## Artifact (${params.artifactPath})`,
									"",
									artifactContent,
								].join("\n");
				} catch (err) {
					job.error = `Could not read specialist skill ${job.skillPath}: ${(err as Error).message}`;
				}
			}

			const reviewerResults = await Promise.all(
				jobs.map(async (job) => {
					if (job.error || !job.systemPrompt) return { id: job.id, skillPath: job.skillPath, error: job.error ?? "unknown error" };
					const result = await runPiSubprocess({
						label: `review-${job.id}`,
						systemPrompt: job.systemPrompt,
						task: `Review ${params.artifactPath} per the criteria above. Return only your findings.`,
						model: params.model,
						cwd: ctx.cwd,
						signal,
					});
					return { id: job.id, skillPath: job.skillPath, result };
				}),
			);

			const findingsBlocks = reviewerResults.map((r) => {
				if ("error" in r && r.error) return `### ${r.id}\n\nFAILED: ${r.error}`;
				const { result } = r as { id: string; result: any };
				const failed = isFailed(result);
				const body = failed ? `FAILED: ${result.errorMessage || result.stderr || "(no output)"}` : result.output || "(no output)";
				return `### ${r.id}\n\n${body}`;
			});

			const convergencePrompt = [
				"You are the mandatory convergence step of general:review's Journey (step 3).",
				"Below are raw findings from every composed reviewer for one artifact.",
				"Perform, in order:",
				"1. VERIFY each candidate finding against the actual artifact (re-read it; trace the claim). Drop what does not hold.",
				"2. DEDUPLICATE findings more than one reviewer raised.",
				"3. SEVERITY-RANK the survivors (High/Medium/Low).",
				"Output only the verified, deduplicated, ranked list. Do not fix anything.",
				"",
				`## Artifact (${params.artifactPath})`,
				"",
				artifactContent,
				"",
				"## Raw reviewer findings",
				"",
				findingsBlocks.join("\n\n"),
			].join("\n");

			const convergence = await runPiSubprocess({
				label: "review-converge",
				systemPrompt: convergencePrompt,
				task: `Converge the reviewer findings for ${params.artifactPath} per the instructions above.`,
				model: params.model,
				cwd: ctx.cwd,
				signal,
			});

			const anyReviewerFailed = reviewerResults.some((r) => ("error" in r && r.error) || ("result" in r && isFailed((r as any).result)));
			const convergenceFailed = isFailed(convergence);

			const header = `Review of ${params.artifactPath} — ${jobs.length} reviewer(s) composed, converged findings below`;
			const body = convergenceFailed
				? `Convergence FAILED: ${convergence.errorMessage || convergence.stderr || "(no output)"}`
				: convergence.output || "(no output)";

			return {
				content: [{ type: "text", text: `${header}\n\n${body}` }],
				isError: anyReviewerFailed || convergenceFailed,
				details: { artifactPath: params.artifactPath, reviewerResults, convergence },
			};
		},
	});
}
