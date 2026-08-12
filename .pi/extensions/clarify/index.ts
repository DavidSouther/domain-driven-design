/**
 * Clarify: a general-purpose "I have a question mid-thought" tool. It does
 * not answer inline; it dispatches a fresh, isolated research-and-decide
 * subagent that checks local convention first, uses research_dispatch for
 * anything research can settle, and either answers with evidence or returns
 * a structured escalation instead of guessing past genuine ambiguity. Its
 * status is parsed from a strict contract line, and its note file's
 * existence is verified on disk, rather than trusting free-form text alone.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { loadPrompt } from "../lib/prompts.ts";
import { nextDatedSlug, runPiSubprocess, slugify, todayIso } from "../lib/subprocess.ts";

// Must mirror the skills research_dispatch accepts (research-subagent/index.ts).
const RESEARCH_SKILLS = ["archaeology", "codebase", "dependencies", "domain", "internal", "public", "books", "papers"];

const ClarifyParams = Type.Object({
	question: Type.String({ description: "The exact question that needs clarification." }),
	context: Type.Optional(
		Type.String({
			description:
				"Why this question came up: the file/code/decision it blocks, constraints already known, anything already tried or ruled out.",
		}),
	),
	model: Type.Optional(Type.String({ description: "Model id/pattern the dispatched research-and-decide subagent runs with." })),
});

// The regex half of the contract whose prompt half is lib/prompts/clarify.md
// step 5; breaking either side alone silently degrades every result to
// no_contract. The *last* occurrence wins, in case the subagent quotes the
// contract line before emitting the real one.
const CLARIFY_MARKER = /^CLARIFY:\s*(ANSWERED|NEEDS_HUMAN)\s*$/gim;

interface ParsedClarifyResult {
	status: "answered" | "needs_human" | "no_contract";
	body: string;
}

function parseClarifyOutput(output: string): ParsedClarifyResult {
	const matches = [...output.matchAll(CLARIFY_MARKER)];
	const match = matches[matches.length - 1];
	if (!match) return { status: "no_contract", body: output };
	const status = match[1].toUpperCase() === "ANSWERED" ? "answered" : "needs_human";
	const body = output.slice(match.index! + match[0].length).trim();
	return { status, body: body || output };
}

export default function (pi: ExtensionAPI) {
	pi.registerTool({
		name: "clarify",
		label: "Clarify",
		description: [
			"Use when a question comes up mid-thinking that you cannot confidently answer from what is already in context —",
			"a style/convention question, something research (public, internal, domain, or codebase) could settle, or a",
			"business/preference decision that may already be recorded internally (Slack, Confluence, Linear, Notion, tickets).",
			"Dispatches an isolated research-and-decide subagent that checks local convention, uses research_dispatch (including",
			"the internal skill for business questions) as needed, and either answers with evidence or returns a structured",
			"escalation (question, contradicting/unclear findings, recommended answer) for you to relay to the user — it does not",
			"guess past genuine ambiguity, and it does not escalate a business question without first checking whether the",
			"decision was already made and documented.",
		].join(" "),
		parameters: ClarifyParams,

		async execute(_toolCallId, params, signal, onUpdate, ctx) {
			const parentDir = path.join(ctx.cwd, ".ailly", "clarify");
			await fs.promises.mkdir(parentDir, { recursive: true });
			const dirName = nextDatedSlug(parentDir, todayIso(), slugify(params.question));
			const notePath = path.join(parentDir, `${dirName}.md`);

			const task = [
				`Question: ${params.question}`,
				params.context ? `Context: ${params.context}` : undefined,
			]
				.filter(Boolean)
				.join("\n");

			const run = await runPiSubprocess({
				label: "clarify",
				systemPrompt: loadPrompt("clarify", { notePath, researchSkills: RESEARCH_SKILLS.join(", ") }),
				task,
				model: params.model,
				cwd: ctx.cwd,
				signal,
				onProgress: (lines) => onUpdate?.({ content: [{ type: "text", text: `Clarifying: ${params.question}\n\n${lines.join("\n")}` }] }),
			});

			const noteFound = fs.existsSync(notePath);
			if (run.exitCode !== 0 || run.stopReason === "error") {
				return {
					content: [{ type: "text", text: `Clarify's subagent failed: ${run.errorMessage || run.stderr || "(no output)"}` }],
					isError: true,
					details: { question: params.question, notePath: noteFound ? notePath : null, run },
				};
			}

			const parsed = parseClarifyOutput(run.output);
			if (ctx.hasUI && parsed.status !== "answered") {
				ctx.ui.notify(`Clarify needs your input: ${params.question}`, "warning");
			}

			const contractWarning =
				parsed.status === "no_contract"
					? "Clarify's subagent did not end with the CLARIFY: ANSWERED/NEEDS_HUMAN contract line — treating this as unresolved rather than trusting it silently.\n\n"
					: "";
			const header =
				parsed.status === "answered"
					? `Clarify answered: ${params.question}`
					: `Clarify could not resolve this with confidence — please advise: ${params.question}`;
			const noteLine = noteFound ? `Note: ${notePath}` : "Note: NOT FOUND — the subagent did not write the contract file, verify manually.";

			return {
				content: [{ type: "text", text: `${header}\n${noteLine}\n\n${contractWarning}${parsed.body}` }],
				details: {
					question: params.question,
					status: parsed.status,
					notePath: noteFound ? notePath : null,
					run,
				},
			};
		},
	});
}
