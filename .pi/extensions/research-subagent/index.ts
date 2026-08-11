/**
 * Research Dispatch Workflow
 *
 * Models `research:using-research` as a dedicated pi tool instead of leaving
 * its mechanics to model orchestration. The skill's own routing table
 * ("which question type maps to which research skill") stays a judgment
 * call for the calling model — that is genuine language understanding, not
 * busywork. What this tool takes over is everything downstream of that
 * choice, which is exactly where prose-only orchestration tends to drift:
 *
 * - **Notes-folder naming.** `YYYY-MM-DD-<letter>-<topic>` requires knowing
 *   today's date and scanning existing folders for the next free letter.
 *   Models get this wrong in ordinary ways: stale dates, timezone slips, or
 *   picking a letter another topic already used today. This tool computes
 *   it deterministically (see `nextDatedSlug` in `../lib/subprocess.ts`).
 * - **Isolation.** Each dispatched skill gets its own subprocess reading
 *   only that skill's `SKILL.md`, not the `using-research` router or any
 *   sibling skill's file — the isolation the skill package asks for but
 *   cannot enforce on itself.
 * - **Parallel dispatch.** "Combining Skills" in `using-research` asks the
 *   caller to remember to fan out and synthesize. Passing multiple `skills`
 *   dispatches them concurrently in one tool call; the model never has to
 *   remember to issue N separate Task calls for a combined question.
 * - **Contract verification.** Every research skill promises to write
 *   `<skill>.md` into the notes folder. This tool checks that the file
 *   actually landed there after the subprocess exits, instead of trusting
 *   the child's self-report.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { createProgressMultiplexer, isFailed, nextDatedSlug, runPiSubprocess, slugify, todayIso } from "../lib/subprocess.ts";

const EXTENSION_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(EXTENSION_DIR, "..", "..", "..");

const SKILLS: Record<string, string> = {
	archaeology: "research/skills/archaeology/SKILL.md",
	codebase: "research/skills/codebase/SKILL.md",
	dependencies: "research/skills/dependencies/SKILL.md",
	domain: "research/skills/domain/SKILL.md",
	internal: "research/skills/internal/SKILL.md",
	public: "research/skills/public/SKILL.md",
	books: "research/skills/books/SKILL.md",
	papers: "research/skills/papers/SKILL.md",
};

const SkillEnum = Object.keys(SKILLS) as [string, ...string[]];

const ResearchDispatchParams = Type.Object({
	skills: Type.Array(
		Type.Union(SkillEnum.map((name) => Type.Literal(name))),
		{
			minItems: 1,
			description:
				"One or more research skills to dispatch. More than one runs them concurrently in this single call (the 'Combining Skills' pattern), each in its own isolated subprocess.",
		},
	),
	question: Type.String({ description: "The research question/task given to every dispatched skill." }),
	topic: Type.Optional(
		Type.String({
			description:
				"Short topic used to name the default notes folder slug when notesFolder is omitted. Defaults to a slug of the question.",
		}),
	),
	notesFolder: Type.Optional(
		Type.String({
			description:
				"Explicit notes folder (e.g. an Ailly development session's <session>/research/ folder). When omitted, defaults to a freshly computed .ailly/research/YYYY-MM-DD-<letter>-<topic>/ folder.",
		}),
	),
	model: Type.Optional(Type.String({ description: "Model id/pattern each dispatched skill subprocess runs with." })),
});

function resolveNotesFolder(cwd: string, params: { notesFolder?: string; topic?: string; question: string }): string {
	if (params.notesFolder) {
		const resolved = path.resolve(cwd, params.notesFolder);
		fs.mkdirSync(resolved, { recursive: true });
		return resolved;
	}
	const parentDir = path.join(cwd, ".ailly", "research");
	fs.mkdirSync(parentDir, { recursive: true });
	const slug = slugify(params.topic || params.question);
	const dirName = nextDatedSlug(parentDir, todayIso(), slug);
	const resolved = path.join(parentDir, dirName);
	fs.mkdirSync(resolved, { recursive: true });
	return resolved;
}

export default function (pi: ExtensionAPI) {
	pi.registerTool({
		name: "research_dispatch",
		label: "Research Dispatch",
		description: [
			"Dispatch one or more research:* skills as isolated pi subprocesses.",
			"Models research:using-research's downstream mechanics (notes-folder",
			"naming, isolation, parallel dispatch, contract verification) as code",
			"instead of leaving them to the orchestrating model. Skill selection",
			"itself (which research skill fits the question) stays your call.",
			`Available skills: ${SkillEnum.join(", ")}.`,
		].join(" "),
		parameters: ResearchDispatchParams,

		async execute(_toolCallId, params, signal, onUpdate, ctx) {
			const notesFolder = resolveNotesFolder(ctx.cwd, params);
			const progress = createProgressMultiplexer((text) => onUpdate?.({ content: [{ type: "text", text: `Notes folder: ${notesFolder}\n\n${text}` }] }));

			const runs = await Promise.all(
				params.skills.map(async (skill) => {
					const relPath = SKILLS[skill];
					const absPath = path.join(REPO_ROOT, relPath);
					let skillBody: string;
					try {
						skillBody = await fs.promises.readFile(absPath, "utf-8");
					} catch (err) {
						return {
							skill,
							relPath,
							notesFile: null as string | null,
							error: `Could not read skill ${relPath}: ${(err as Error).message}`,
						};
					}

					const systemPrompt = [
						"You are an isolated research subagent, dispatched by research:using-research.",
						`Read only the skill below (sourced from ${relPath}) and execute it exactly.`,
						"Do not read any other research:* skill or the using-research router in this process.",
						`Write your findings file into this exact notes folder: ${notesFolder}`,
						"",
						skillBody,
					].join("\n");

					const result = await runPiSubprocess({
						label: skill,
						systemPrompt,
						task: params.question,
						model: params.model,
						cwd: ctx.cwd,
						signal,
						onProgress: progress.lane(skill),
					});

					const notesFile = path.join(notesFolder, `${skill}.md`);
					const wroteNotes = fs.existsSync(notesFile);

					return {
						skill,
						relPath,
						notesFile: wroteNotes ? notesFile : null,
						result,
					};
				}),
			);

			const sections = runs.map((run) => {
				if ("error" in run && run.error) return `## ${run.skill}\n\nFAILED: ${run.error}`;
				const { result, notesFile } = run as { skill: string; relPath: string; notesFile: string | null; result: any };
				const failed = isFailed(result);
				const noteLine = notesFile
					? `Notes: ${notesFile}`
					: "Notes: NOT FOUND — the subagent did not write the contract file, verify manually.";
				const body = failed
					? `FAILED: ${result.errorMessage || result.stderr || "(no output)"}`
					: result.output || "(no output)";
				return `## ${run.skill} (${run.relPath})\n\n${noteLine}\n\n${body}`;
			});

			const anyFailed = runs.some((run) => "error" in run && run.error) || runs.some((run) => "result" in run && isFailed((run as any).result));

			return {
				content: [{ type: "text", text: `Notes folder: ${notesFolder}\n\n${sections.join("\n\n")}` }],
				isError: anyFailed,
				details: { notesFolder, runs },
			};
		},
	});
}
