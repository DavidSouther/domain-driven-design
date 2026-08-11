/**
 * Ailly Subagent Runner
 *
 * A pi-native `Task` equivalent for the `developer:ailly` lifecycle coordinator
 * (and any other skill in this repository that needs isolated subagent
 * dispatch, e.g. `general:dispatching-agents`).
 *
 * Spawns a separate `pi` process per dispatch, giving it an isolated context
 * window. Unlike the generic pi subagent example, this tool does not depend
 * on `.pi/agents/` or `~/.pi/agent/agents/` discovery: every reference file it
 * can dispatch is resolved *relative to this extension's own module path*, so
 * it keeps working no matter where this package is installed (`pi install
 * git:...`, a local path, or straight from this checkout) and no matter what
 * the caller's cwd is. That is the whole point: Ailly's phase-isolation
 * contract ("read only the one matching references/<phase>.md") has to
 * survive being installed into someone else's project, not just work while
 * developing this repo.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { isFailed, runPiSubprocess } from "../lib/subprocess.ts";

// Repo root is three levels up from .pi/extensions/ailly-subagent/index.ts.
const EXTENSION_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(EXTENSION_DIR, "..", "..", "..");

/**
 * Canonical reference names Ailly (and other skills) dispatch by. Each maps
 * to a file resolved relative to REPO_ROOT, not to the caller's cwd, so the
 * mapping holds regardless of where this package ends up installed.
 */
const REFERENCES: Record<string, string> = {
	research: "developer/skills/ailly/references/phases/research.md",
	design: "developer/skills/ailly/references/phases/design.md",
	plan: "developer/skills/ailly/references/phases/plan.md",
	"red-green-refactor": "developer/skills/ailly/references/phases/red-green-refactor.md",
	build: "developer/skills/ailly/references/phases/red-green-refactor.md",
	cleanup: "developer/skills/ailly/references/phases/cleanup.md",
	thinking: "developer/skills/ailly/references/abilities/thinking.md",
	refactor: "developer/skills/ailly/references/abilities/refactor.md",
	initialize: "developer/skills/ailly/references/abilities/initialize.md",
	"intent-review": "developer/skills/ailly/references/abilities/intent-review.md",
};

const ReferenceEnum = Object.keys(REFERENCES) as [string, ...string[]];

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
			"initialize/intent-review whenever dispatch is warranted. Reference",
			`paths resolve relative to this extension's own install location`,
			`(currently ${REPO_ROOT}), not the caller's cwd, so this keeps working`,
			"after the package is installed anywhere.",
			`Available references: ${ReferenceEnum.join(", ")}.`,
		].join(" "),
		parameters: AillySubagentParams,

		async execute(_toolCallId, params, signal, _onUpdate, ctx) {
			const relPath = REFERENCES[params.reference];
			const absPath = path.join(REPO_ROOT, relPath);

			let referenceBody: string;
			try {
				referenceBody = await fs.promises.readFile(absPath, "utf-8");
			} catch (err) {
				return {
					content: [{ type: "text", text: `Could not read reference ${relPath}: ${(err as Error).message}` }],
					isError: true,
					details: { reference: params.reference, referencePath: relPath },
				};
			}

			const systemPrompt = [
				"You are an isolated Ailly phase/ability subagent, dispatched by developer:ailly.",
				`Read only the reference below (sourced from ${relPath}) and execute it exactly.`,
				"Do not read any other developer:ailly phase or ability reference in this process.",
				"",
				referenceBody,
			].join("\n");

			const result = await runPiSubprocess({
				label: params.reference,
				systemPrompt,
				task: params.task,
				model: params.model,
				cwd: ctx.cwd,
				signal,
			});

			const header = `Ailly subagent [${params.reference}] via ${relPath}${result.model ? ` (model: ${result.model})` : ""}`;
			const body = isFailed(result)
				? `FAILED: ${result.errorMessage || result.stderr || "(no output)"}`
				: result.output || "(no output)";

			return {
				content: [{ type: "text", text: `${header}\n\n${body}` }],
				isError: isFailed(result),
				details: { reference: params.reference, referencePath: relPath, ...result },
			};
		},
	});
}
