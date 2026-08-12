/**
 * Shared general:review Dispatch + Converge implementation, used by both
 * `review_run` and `ailly_quick_loop`'s automatic per-phase reviews.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { loadPrompt } from "./prompts.ts";
import { findSkillByName, specialistSkillName } from "./skills.ts";
import { createProgressMultiplexer, isFailed, runPiSubprocess, type SubprocessRunResult } from "./subprocess.ts";

const REVIEW_SKILL_PATH = "general/skills/review/SKILL.md";

/** Body of the `## <heading>` section (exact match, stops at the next `##`); "" on miss. */
export function extractSection(markdown: string, heading: string): string {
	const lines = markdown.split("\n");
	const startIndex = lines.findIndex((line) => line.trim() === `## ${heading}`);
	if (startIndex === -1) return "";
	const rest = lines.slice(startIndex + 1);
	const endOffset = rest.findIndex((line) => /^##\s+/.test(line));
	const body = endOffset === -1 ? rest : rest.slice(0, endOffset);
	return body.join("\n").trim();
}

export interface ReviewerOutcome {
	id: string;
	skillPath: string | null;
	error?: string;
	run?: SubprocessRunResult;
}

export interface RunReviewOptions {
	artifactPath: string;
	specialists?: string[];
	model?: string;
	cwd: string;
	repoRoot: string;
	signal?: AbortSignal;
	/** Combined live progress across every reviewer lane, then the convergence lane. */
	onProgress?: (combinedText: string) => void;
}

export interface RunReviewResult {
	artifactPath: string;
	reviewerOutcomes: ReviewerOutcome[];
	convergence: SubprocessRunResult;
	anyReviewerFailed: boolean;
	convergenceFailed: boolean;
}

/**
 * Run general:review's Dispatch and mandatory Converge for one artifact: the
 * base reviewer plus any named specialists, in parallel, isolated
 * subprocesses, followed by one dedicated convergence subprocess.
 *
 * Returns `{ error }` only when an input file cannot be read; reviewer or
 * convergence subprocess failures surface on the success shape via
 * `anyReviewerFailed`/`convergenceFailed`.
 */
export async function runReview(opts: RunReviewOptions): Promise<RunReviewResult | { error: string }> {
	const { artifactPath, specialists, model, cwd, repoRoot, signal, onProgress } = opts;
	const progress = onProgress ? createProgressMultiplexer(onProgress) : undefined;
	const artifactAbsPath = path.resolve(cwd, artifactPath);
	let artifactContent: string;
	try {
		artifactContent = await fs.promises.readFile(artifactAbsPath, "utf-8");
	} catch (err) {
		return { error: `Could not read artifact ${artifactPath}: ${(err as Error).message}` };
	}

	let reviewSkillText: string;
	try {
		reviewSkillText = await fs.promises.readFile(path.join(repoRoot, REVIEW_SKILL_PATH), "utf-8");
	} catch (err) {
		return { error: `Could not read ${REVIEW_SKILL_PATH}: ${(err as Error).message}` };
	}
	const baseRubric = extractSection(reviewSkillText, "Base Reviewer");
	if (!baseRubric) return { error: `No "## Base Reviewer" section found in ${REVIEW_SKILL_PATH}` };

	type ReviewerJob = { id: string; skillPath: string | null; systemPrompt: string | null; error?: string };

	const jobs: ReviewerJob[] = [
		{
			id: "base",
			skillPath: path.join(repoRoot, REVIEW_SKILL_PATH),
			systemPrompt: loadPrompt("review-base", { baseRubric, artifactPath, artifactContent }),
		},
		...(specialists ?? []).map((specialist): ReviewerJob => {
			const name = specialistSkillName(specialist);
			const absPath = findSkillByName(name, repoRoot, cwd);
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
		if (job.error || job.systemPrompt) continue;
		try {
			const skillBody = await fs.promises.readFile(job.skillPath!, "utf-8");
			job.systemPrompt = loadPrompt("review-specialist", { id: job.id, skillBody, artifactPath, artifactContent });
		} catch (err) {
			job.error = `Could not read specialist skill ${job.skillPath}: ${(err as Error).message}`;
		}
	}

	const reviewerOutcomes: ReviewerOutcome[] = await Promise.all(
		jobs.map(async (job): Promise<ReviewerOutcome> => {
			if (job.error || !job.systemPrompt) return { id: job.id, skillPath: job.skillPath, error: job.error ?? "unknown error" };
			const run = await runPiSubprocess({
				label: `review-${job.id}`,
				systemPrompt: job.systemPrompt,
				task: `Review ${artifactPath} per the criteria above. Return only your findings.`,
				model,
				cwd,
				signal,
				onProgress: progress?.lane(job.id),
			});
			return { id: job.id, skillPath: job.skillPath, run };
		}),
	);

	// Failed reviewers still feed a FAILED block into convergence rather than
	// aborting: convergence is mandatory even when some reviewers fail.
	const findingsBlocks = reviewerOutcomes.map((r) => {
		if (r.error) return `### ${r.id}\n\nFAILED: ${r.error}`;
		const failed = isFailed(r.run!);
		const body = failed ? `FAILED: ${r.run!.errorMessage || r.run!.stderr || "(no output)"}` : r.run!.output || "(no output)";
		return `### ${r.id}\n\n${body}`;
	});

	const convergence = await runPiSubprocess({
		label: "review-converge",
		systemPrompt: loadPrompt("review-converge", { artifactPath, artifactContent, findings: findingsBlocks.join("\n\n") }),
		task: `Converge the reviewer findings for ${artifactPath} per the instructions above.`,
		model,
		cwd,
		signal,
		onProgress: progress?.lane("converge"),
	});

	return {
		artifactPath,
		reviewerOutcomes,
		convergence,
		anyReviewerFailed: reviewerOutcomes.some((r) => r.error || isFailed(r.run!)),
		convergenceFailed: isFailed(convergence),
	};
}
