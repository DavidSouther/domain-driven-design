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

import { spawn } from "node:child_process";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { Message } from "@earendil-works/pi-ai";
import { withFileMutationQueue, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

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

interface UsageStats {
	input: number;
	output: number;
	cacheRead: number;
	cacheWrite: number;
	cost: number;
	contextTokens: number;
	turns: number;
}

interface RunResult {
	reference: string;
	referencePath: string;
	exitCode: number;
	output: string;
	stderr: string;
	usage: UsageStats;
	model?: string;
	stopReason?: string;
	errorMessage?: string;
}

function emptyUsage(): UsageStats {
	return { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, cost: 0, contextTokens: 0, turns: 0 };
}

function getFinalOutput(messages: Message[]): string {
	for (let i = messages.length - 1; i >= 0; i--) {
		const msg = messages[i];
		if (msg.role === "assistant") {
			for (const part of msg.content) {
				if (part.type === "text") return part.text;
			}
		}
	}
	return "";
}

/** Resolve the same command used to invoke the current pi process. */
function getPiInvocation(args: string[]): { command: string; args: string[] } {
	const currentScript = process.argv[1];
	const isBunVirtualScript = currentScript?.startsWith("/$bunfs/root/");
	if (currentScript && !isBunVirtualScript && fs.existsSync(currentScript)) {
		return { command: process.execPath, args: [currentScript, ...args] };
	}
	const execName = path.basename(process.execPath).toLowerCase();
	const isGenericRuntime = /^(node|bun)(\.exe)?$/.test(execName);
	if (!isGenericRuntime) return { command: process.execPath, args };
	return { command: "pi", args };
}

async function writePromptToTempFile(name: string, prompt: string): Promise<{ dir: string; filePath: string }> {
	const tmpDir = await fs.promises.mkdtemp(path.join(os.tmpdir(), "ailly-subagent-"));
	const safeName = name.replace(/[^\w.-]+/g, "_");
	const filePath = path.join(tmpDir, `prompt-${safeName}.md`);
	await withFileMutationQueue(filePath, async () => {
		await fs.promises.writeFile(filePath, prompt, { encoding: "utf-8", mode: 0o600 });
	});
	return { dir: tmpDir, filePath };
}

async function runReference(
	reference: string,
	referencePath: string,
	referenceBody: string,
	task: string,
	model: string | undefined,
	cwd: string,
	signal: AbortSignal | undefined,
): Promise<RunResult> {
	const args: string[] = ["--mode", "json", "-p", "--no-session"];
	if (model) args.push("--model", model);

	const result: RunResult = {
		reference,
		referencePath,
		exitCode: 0,
		output: "",
		stderr: "",
		usage: emptyUsage(),
		model,
	};

	let tmpDir: string | null = null;
	let tmpPath: string | null = null;
	try {
		const preamble = [
			"You are an isolated Ailly phase/ability subagent, dispatched by developer:ailly.",
			`Read only the reference below (sourced from ${referencePath}) and execute it exactly.`,
			"Do not read any other developer:ailly phase or ability reference in this process.",
			"",
			referenceBody,
		].join("\n");
		const tmp = await writePromptToTempFile(reference, preamble);
		tmpDir = tmp.dir;
		tmpPath = tmp.filePath;
		args.push("--append-system-prompt", tmpPath);
		args.push(task);

		const messages: Message[] = [];
		let wasAborted = false;

		result.exitCode = await new Promise<number>((resolve) => {
			const invocation = getPiInvocation(args);
			const proc = spawn(invocation.command, invocation.args, {
				cwd,
				shell: false,
				stdio: ["ignore", "pipe", "pipe"],
			});
			let buffer = "";

			const processLine = (line: string) => {
				if (!line.trim()) return;
				let event: any;
				try {
					event = JSON.parse(line);
				} catch {
					return;
				}
				if (event.type === "message_end" && event.message) {
					const msg = event.message as Message;
					messages.push(msg);
					if (msg.role === "assistant") {
						result.usage.turns++;
						const usage = msg.usage;
						if (usage) {
							result.usage.input += usage.input || 0;
							result.usage.output += usage.output || 0;
							result.usage.cacheRead += usage.cacheRead || 0;
							result.usage.cacheWrite += usage.cacheWrite || 0;
							result.usage.cost += usage.cost?.total || 0;
							result.usage.contextTokens = usage.totalTokens || 0;
						}
						if (!result.model && msg.model) result.model = msg.model;
						if (msg.stopReason) result.stopReason = msg.stopReason;
						if (msg.errorMessage) result.errorMessage = msg.errorMessage;
					}
				}
			};

			proc.stdout.on("data", (data) => {
				buffer += data.toString();
				const lines = buffer.split("\n");
				buffer = lines.pop() || "";
				for (const line of lines) processLine(line);
			});
			proc.stderr.on("data", (data) => {
				result.stderr += data.toString();
			});
			proc.on("close", (code) => {
				if (buffer.trim()) processLine(buffer);
				resolve(code ?? 0);
			});
			proc.on("error", () => resolve(1));

			if (signal) {
				const kill = () => {
					wasAborted = true;
					proc.kill("SIGTERM");
					setTimeout(() => {
						if (!proc.killed) proc.kill("SIGKILL");
					}, 5000);
				};
				if (signal.aborted) kill();
				else signal.addEventListener("abort", kill, { once: true });
			}
		});

		result.output = getFinalOutput(messages);
		if (wasAborted) throw new Error("Ailly subagent was aborted");
		return result;
	} finally {
		if (tmpPath) {
			try {
				fs.unlinkSync(tmpPath);
			} catch {
				/* ignore */
			}
		}
		if (tmpDir) {
			try {
				fs.rmdirSync(tmpDir);
			} catch {
				/* ignore */
			}
		}
	}
}

function isFailed(result: RunResult): boolean {
	return result.exitCode !== 0 || result.stopReason === "error";
}

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

			const result = await runReference(
				params.reference,
				relPath,
				referenceBody,
				params.task,
				params.model,
				ctx.cwd,
				signal,
			);

			const header = `Ailly subagent [${params.reference}] via ${relPath}${result.model ? ` (model: ${result.model})` : ""}`;
			const body = isFailed(result)
				? `FAILED: ${result.errorMessage || result.stderr || "(no output)"}`
				: result.output || "(no output)";

			return {
				content: [{ type: "text", text: `${header}\n\n${body}` }],
				isError: isFailed(result),
				details: result,
			};
		},
	});
}
