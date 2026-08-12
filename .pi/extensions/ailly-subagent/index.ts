/**
 * ailly_subagent: a pi-native `Task` equivalent for the `developer:ailly`
 * lifecycle coordinator. Dispatch mechanics live in `../lib/ailly-phases.ts`.
 */

import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { PHASE_REFERENCES, runAillyReference } from "../lib/ailly-phases.ts";
import { isFailed } from "../lib/subprocess.ts";

const EXTENSION_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(EXTENSION_DIR, "..", "..", "..");

const ReferenceEnum = Object.keys(PHASE_REFERENCES) as [string, ...string[]];

const AillySubagentParams = Type.Object({
	reference: Type.Union(
		ReferenceEnum.map((name) => Type.Literal(name)),
		{
			description:
				"Which developer:ailly phase or ability reference the subagent reads and executes in isolation.",
		},
	),
	task: Type.String({
		description:
			"The instruction for this dispatch: the session folder path plus any phase-specific context the reference needs.",
	}),
	model: Type.Optional(
		Type.String({
			description:
				"Model id/pattern to run the subagent with (mandate-with-announce: set this from general/skills/dispatching-agents/model-selection.md, and announce the choice either way).",
		}),
	),
});

export default function (pi: ExtensionAPI) {
	pi.registerTool({
		name: "ailly_subagent",
		label: "Ailly Subagent",
		description: [
			"Dispatch an isolated pi subprocess that reads exactly one developer:ailly",
			"phase or ability reference and executes it. This is Ailly's Task-tool",
			"equivalent for pi: use it for every phase dispatch (research, design,",
			"plan, red-green-refactor/build, cleanup) and for thinking/refactor/",
			"initialize/intent-review whenever dispatch is warranted. For a full",
			"unattended quick-loop or long-loop run, prefer ailly_quick_loop or",
			"ailly_long_loop_start, which drive this same dispatch sequentially with",
			"review calls wired in. Reference paths resolve relative to this",
			`extension's own install location (currently ${REPO_ROOT}), not the`,
			"caller's cwd, so this keeps working after the package is installed",
			`anywhere. Available references: ${ReferenceEnum.join(", ")}.`,
		].join(" "),
		parameters: AillySubagentParams,

		async execute(_toolCallId, params, signal, onUpdate, ctx) {
			const progressHeader = `Ailly subagent [${params.reference}] via ${PHASE_REFERENCES[params.reference] ?? "?"}`;
			const outcome = await runAillyReference({
				reference: params.reference,
				task: params.task,
				model: params.model,
				cwd: ctx.cwd,
				repoRoot: REPO_ROOT,
				signal,
				onProgress: (recentLines) => onUpdate?.({ content: [{ type: "text", text: `${progressHeader}\n\n${recentLines.join("\n")}` }] }),
			});

			if (outcome.error || !outcome.run) {
				return {
					content: [{ type: "text", text: outcome.error ?? "Unknown failure" }],
					isError: true,
					details: outcome,
				};
			}

			const header = `Ailly subagent [${outcome.reference}] via ${outcome.referencePath}${outcome.run.model ? ` (model: ${outcome.run.model})` : ""}`;
			const body = isFailed(outcome.run)
				? `FAILED: ${outcome.run.errorMessage || outcome.run.stderr || "(no output)"}`
				: outcome.run.output || "(no output)";

			return {
				content: [{ type: "text", text: `${header}\n\n${body}` }],
				isError: isFailed(outcome.run),
				details: outcome,
			};
		},
	});
}
