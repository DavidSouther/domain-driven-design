/**
 * Shared isolated-`pi`-subprocess runner.
 *
 * Every dedicated-workflow tool in this package (`ailly_subagent`,
 * `research_dispatch`, `review_run`) needs the same primitive: spawn a
 * separate `pi` process with a specific system prompt and task, capture its
 * final text output plus usage, and clean up. This module is that primitive,
 * factored out so the workflow-specific tools stay focused on *what* to
 * dispatch (which reference file, which reviewer) rather than *how*.
 */

import { spawn } from "node:child_process";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import type { Message } from "@earendil-works/pi-ai";
import { withFileMutationQueue } from "@earendil-works/pi-coding-agent";

export interface UsageStats {
	input: number;
	output: number;
	cacheRead: number;
	cacheWrite: number;
	cost: number;
	contextTokens: number;
	turns: number;
}

export interface SubprocessRunResult {
	label: string;
	exitCode: number;
	output: string;
	stderr: string;
	usage: UsageStats;
	model?: string;
	stopReason?: string;
	errorMessage?: string;
}

export function emptyUsage(): UsageStats {
	return { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, cost: 0, contextTokens: 0, turns: 0 };
}

export function isFailed(result: SubprocessRunResult): boolean {
	return result.exitCode !== 0 || result.stopReason === "error";
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

function truncate(text: string, max: number): string {
	return text.length > max ? `${text.slice(0, max)}…` : text;
}

/** Render one `tool_execution_start` event as a short, human-scannable line. */
function formatToolCallLine(toolName: string, args: Record<string, unknown>): string {
	switch (toolName) {
		case "bash":
			return `$ ${truncate(String(args.command ?? ""), 100)}`;
		case "read":
			return `read ${args.path ?? "?"}${args.offset ? `:${args.offset}` : ""}`;
		case "write":
			return `write ${args.path ?? "?"}`;
		case "edit":
			return `edit ${args.path ?? "?"}`;
		default: {
			const preview = truncate(JSON.stringify(args ?? {}), 100);
			return `${toolName} ${preview}`;
		}
	}
}

/** Resolve the same command used to invoke the current pi process. */
export function getPiInvocation(args: string[]): { command: string; args: string[] } {
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

async function writePromptToTempFile(label: string, prompt: string): Promise<{ dir: string; filePath: string }> {
	const tmpDir = await fs.promises.mkdtemp(path.join(os.tmpdir(), "pi-workflow-"));
	const safeName = label.replace(/[^\w.-]+/g, "_");
	const filePath = path.join(tmpDir, `prompt-${safeName}.md`);
	await withFileMutationQueue(filePath, async () => {
		await fs.promises.writeFile(filePath, prompt, { encoding: "utf-8", mode: 0o600 });
	});
	return { dir: tmpDir, filePath };
}

export interface RunPiSubprocessOptions {
	/** Short identifier used in temp-file naming and error messages. */
	label: string;
	/** Full system-prompt text (typically the isolated reference/skill body plus framing). */
	systemPrompt: string;
	/** The task/user message for the child process. */
	task: string;
	/** Model id/pattern passed straight to the child's `--model` flag. */
	model?: string;
	cwd: string;
	signal?: AbortSignal;
	/**
	 * Called with a rolling, human-readable transcript of the child's recent
	 * tool calls and assistant text as they happen, so a caller's own tool
	 * `onUpdate` can replace a static "Working..." spinner with a live view
	 * into what the isolated subagent is actually doing.
	 */
	onProgress?: (recentLines: string[]) => void;
}

/**
 * Spawn an isolated `pi` subprocess, feed it `systemPrompt` + `task`, and
 * collect its final assistant text plus usage. This is the mechanism behind
 * every dedicated workflow tool's subagent dispatch: real process isolation,
 * not a same-session role-play.
 */
export async function runPiSubprocess(opts: RunPiSubprocessOptions): Promise<SubprocessRunResult> {
	const { label, systemPrompt, task, model, cwd, signal, onProgress } = opts;
	const args: string[] = ["--mode", "json", "-p", "--no-session"];
	if (model) args.push("--model", model);

	const result: SubprocessRunResult = {
		label,
		exitCode: 0,
		output: "",
		stderr: "",
		usage: emptyUsage(),
		model,
	};

	let tmpDir: string | null = null;
	let tmpPath: string | null = null;
	try {
		const tmp = await writePromptToTempFile(label, systemPrompt);
		tmpDir = tmp.dir;
		tmpPath = tmp.filePath;
		args.push("--append-system-prompt", tmpPath, task);

		const messages: Message[] = [];
		let wasAborted = false;
		const recentLines: string[] = [];
		const pushProgress = (line: string) => {
			if (!onProgress) return;
			recentLines.push(line);
			if (recentLines.length > 20) recentLines.shift();
			onProgress([...recentLines]);
		};

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
				if (event.type === "tool_execution_start" && event.toolName) {
					pushProgress(formatToolCallLine(event.toolName, event.args ?? {}));
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
						for (const part of msg.content) {
							if (part.type === "text" && part.text.trim()) pushProgress(`\u{1F4AC} ${truncate(part.text.trim(), 300)}`);
						}
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
		if (wasAborted) throw new Error(`Pi subprocess [${label}] was aborted`);
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

/**
 * Deterministic `YYYY-MM-DD-<letter>-<slug>` folder naming, shared by every
 * workflow that follows Ailly's session-folder / research-notes convention.
 * Doing this in code (not asking the orchestrating model to compute "today's
 * date" and scan for the next free letter) removes a step models reliably
 * get wrong: stale dates, wrong timezone, or reusing an already-taken letter.
 */
export function nextDatedSlug(parentDir: string, date: string, topicSlug: string): string {
	let existingLetters: string[] = [];
	try {
		existingLetters = fs
			.readdirSync(parentDir, { withFileTypes: true })
			.filter((e) => e.isDirectory())
			.map((e) => e.name)
			.filter((name) => name.startsWith(`${date}-`))
			.map((name) => name.slice(date.length + 1, date.length + 2))
			.filter((letter) => /^[A-Z]$/.test(letter));
	} catch {
		existingLetters = [];
	}

	let letter = "A";
	for (let code = 65; code <= 90; code++) {
		const candidate = String.fromCharCode(code);
		if (!existingLetters.includes(candidate)) {
			letter = candidate;
			break;
		}
	}
	return `${date}-${letter}-${topicSlug}`;
}

export function slugify(text: string, maxWords = 6): string {
	const slug = text
		.toLowerCase()
		.split(/\s+/)
		.slice(0, maxWords)
		.join(" ")
		.replace(/[^a-z0-9\s-]/g, "")
		.trim()
		.replace(/\s+/g, "-")
		.replace(/-+/g, "-");
	return slug || "topic";
}

export function todayIso(): string {
	return new Date().toISOString().slice(0, 10);
}

/**
 * Combine several concurrent subprocesses' `onProgress` streams into one
 * live view, keyed by a caller-chosen lane id (e.g. a skill name or
 * reviewer id). Used by every tool that dispatches more than one
 * `runPiSubprocess` in parallel (`research_dispatch`, `review_run`) so the
 * live "Working..." replacement shows all lanes at once, not just whichever
 * one last called back.
 */
export function createProgressMultiplexer(onUpdate: (combinedText: string) => void) {
	const lanes = new Map<string, string[]>();
	const render = () => {
		const combined = Array.from(lanes.entries())
			.map(([id, lines]) => `## ${id}\n${lines.join("\n")}`)
			.join("\n\n");
		onUpdate(combined);
	};
	return {
		lane(id: string): (recentLines: string[]) => void {
			return (recentLines: string[]) => {
				lanes.set(id, recentLines);
				render();
			};
		},
	};
}
