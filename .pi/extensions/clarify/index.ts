/**
 * Clarify
 *
 * A general-purpose "I have a question mid-thought" tool, usable by any
 * (sub)agent in this project — the top-level interactive session, or any
 * subagent dispatched by ailly_subagent/research_dispatch/review_run/
 * ailly_quick_loop/ailly_long_loop_start, since all of those are just `pi`
 * processes that have this tool available too.
 *
 * It does not answer the question itself inline. It dispatches a fresh,
 * isolated subagent — with research_dispatch, ailly_subagent, and the
 * native read/grep/bash tools available to it — whose job is to work the
 * question the way a person would: check local convention/style first
 * (often the fastest path for "how should this look" questions), then reach
 * for the relevant research:* skill(s) (public, internal, domain, codebase,
 * dependencies, archaeology, papers, books) for anything research can
 * settle, applying the same Jeopardy-search and falsification discipline
 * those skills already carry.
 *
 * Some questions cannot be settled by research at all — a preference, a
 * business decision, or something the evidence leaves genuinely
 * contradictory or absent even after investigating. For those, the
 * dispatched subagent does not guess: it returns a structured escalation
 * (question, the contradicting/unclear findings, and its best-guess
 * recommendation) instead of a confident answer, verified against a written
 * note rather than trusted from its own return text — this tool's
 * equivalent of long-loop.md's research-and-decide reviewer contract,
 * generalized to any ad hoc question instead of only Ailly's draft gates.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { nextDatedSlug, runPiSubprocess, slugify, todayIso } from "../lib/subprocess.ts";

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

const CLARIFY_MARKER = /^CLARIFY:\s*(ANSWERED|NEEDS_HUMAN)\s*$/im;

interface ParsedClarifyResult {
	status: "answered" | "needs_human" | "no_contract";
	body: string;
}

function parseClarifyOutput(output: string): ParsedClarifyResult {
	const match = CLARIFY_MARKER.exec(output);
	if (!match) return { status: "no_contract", body: output };
	const status = match[1].toUpperCase() === "ANSWERED" ? "answered" : "needs_human";
	const body = output.slice(match.index + match[0].length).trim();
	return { status, body: body || output };
}

function buildSystemPrompt(notePath: string): string {
	return [
		"You are Clarify: an isolated research-and-decide subagent answering one specific question that came up during",
		"another (sub)agent's work. You are not that agent's whole session — you have only the question and context below,",
		"plus your own tools. Work the question the way a careful person would, then report back in a strict format so the",
		"caller can act on it deterministically.",
		"",
		"## Process",
		"",
		"1. Classify the question first:",
		"   - **Local style/convention** (\"how should this look/be named/be structured here\") — check this repo directly",
		`     first: read AGENTS.md/DEVELOPMENT.md/README.md, grep for existing examples, and consult the \`patterns:using-patterns\``,
		"     or other loaded skills before reaching for external research. Local precedent usually settles these fastest.",
		"   - **Factual/external, domain, historical, or dependency-related** — dispatch the `research_dispatch` tool with",
		`     whichever skill(s) fit (${RESEARCH_SKILLS.join(", ")}); pass more than one in the same call when the question`,
		"     spans skills (e.g. \"why does this exist and what does it do\" -> dependencies + archaeology). Each skill already",
		"     applies Jeopardy-search query expansion and, for load-bearing claims, a falsification pass — you do not need to",
		"     re-derive that discipline yourself.",
		"   - **Preference, business decision, or anything only the project owner has the authority to decide** — do not",
		"     spend a research round pretending this is discoverable. Go straight to step 3's NEEDS_HUMAN branch, but still",
		"     give your best-guess recommendation.",
		"2. If research or local convention gives a clear, sourced answer with no real contradiction, that is your answer.",
		"3. Decide ANSWERED vs NEEDS_HUMAN. Use NEEDS_HUMAN when any of these hold, even after investigating:",
		"   - **Irreversible or high-blast-radius**: acting on the wrong guess here is not cheaply undone.",
		"   - **Authority-only**: the question is a preference or business decision no amount of research settles.",
		"   - **Underdetermined or contradictory**: local convention and research disagree, or neither says anything usable.",
		"   Do not guess past these triggers. A wrong confident answer is worse than an honest escalation.",
		`4. Write a note to this exact path: ${notePath}`,
		"   Markdown, with sections: `# Clarify: <question>`, `## Status` (Answered/Needs human), `## Findings` (what you",
		"   checked, what you found, contradictions if any), `## Answer` (the answer if ANSWERED) or `## Recommended Answer`",
		"   (your best guess if NEEDS_HUMAN, clearly labeled as unconfirmed), and `## Sources` (files read, skills",
		"   dispatched, commands run).",
		"5. End your final message with exactly one line, verbatim, then the same content as the note body beneath it:",
		"   `CLARIFY: ANSWERED` or `CLARIFY: NEEDS_HUMAN` — nothing else on that line, no extra formatting around it.",
	].join("\n");
}

export default function (pi: ExtensionAPI) {
	pi.registerTool({
		name: "clarify",
		label: "Clarify",
		description: [
			"Use when a question comes up mid-thinking that you cannot confidently answer from what is already in context —",
			"a style/convention question, something research (public, internal, domain, or codebase) could settle, or a",
			"preference/decision only the project owner can make. Dispatches an isolated research-and-decide subagent that",
			"checks local convention, uses research_dispatch as needed, and either answers with evidence or returns a",
			"structured escalation (question, contradicting/unclear findings, recommended answer) for you to relay to the",
			"user — it does not guess past genuine ambiguity or an authority-only decision.",
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
				systemPrompt: buildSystemPrompt(notePath),
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
