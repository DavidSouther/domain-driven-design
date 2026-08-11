/**
 * Shared general:review Dispatch + Converge implementation.
 *
 * Factored out of `review_run` so `ailly_quick_loop` and the long-loop
 * driver can run the same "every artifact gets reviewed, convergence is
 * mandatory" contract automatically after each phase, not only when the
 * top-level model remembers to call the tool itself.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { findSkillByName, specialistSkillName } from "./skills.ts";
import { createProgressMultiplexer, isFailed, runPiSubprocess, type SubprocessRunResult } from "./subprocess.ts";

const REVIEW_SKILL_PATH = "general/skills/review/SKILL.md";

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
 * Run general:review's Dispatch (step 2) and mandatory Converge (step 3) for
 * one artifact: the base reviewer plus any named specialists, in parallel,
 * isolated subprocesses, followed by one dedicated convergence subprocess.
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

	const reviewSkillText = await fs.promises.readFile(path.join(repoRoot, REVIEW_SKILL_PATH), "utf-8");
	const baseRubric = extractSection(reviewSkillText, "Base Reviewer");

	type ReviewerJob = { id: string; skillPath: string | null; systemPrompt: string | null; error?: string };

	const jobs: ReviewerJob[] = [
		{
			id: "base",
			skillPath: path.join(repoRoot, REVIEW_SKILL_PATH),
			systemPrompt: [
				"You are the always-present base reviewer from general:review's composed set.",
				"Evaluate the artifact below against exactly these four criteria. Do not fix",
				"anything. List verified findings ranked by severity (High/Medium/Low).",
				"",
				baseRubric,
				"",
				`## Artifact (${artifactPath})`,
				"",
				artifactContent,
			].join("\n"),
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
							`## Artifact (${artifactPath})`,
							"",
							artifactContent,
						].join("\n");
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

	const findingsBlocks = reviewerOutcomes.map((r) => {
		if (r.error) return `### ${r.id}\n\nFAILED: ${r.error}`;
		const failed = isFailed(r.run!);
		const body = failed ? `FAILED: ${r.run!.errorMessage || r.run!.stderr || "(no output)"}` : r.run!.output || "(no output)";
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
		`## Artifact (${artifactPath})`,
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
