/**
 * Long-loop background-run bookkeeping: spawn the detached `pi` process with
 * its `--mode json` stream redirected to a journal file, and read that
 * journal plus a small status header back deterministically.
 */

import { spawn } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import { getPiInvocation } from "./subprocess.ts";

export interface LongLoopStatus {
	pid: number;
	topic: string;
	sessionFolder: string;
	journalPath: string;
	stderrPath: string;
	model?: string;
	startedAt: string;
	stopped?: boolean;
	stoppedAt?: string;
	stopReason?: string;
}

function statusPath(sessionFolder: string): string {
	return path.join(sessionFolder, "long-loop-status.json");
}

export function readStatus(sessionFolder: string): LongLoopStatus | null {
	try {
		return JSON.parse(fs.readFileSync(statusPath(sessionFolder), "utf-8"));
	} catch {
		return null;
	}
}

export function writeStatus(status: LongLoopStatus): void {
	fs.writeFileSync(statusPath(status.sessionFolder), JSON.stringify(status, null, 2), "utf-8");
}

export function isPidAlive(pid: number): boolean {
	try {
		process.kill(pid, 0);
		return true;
	} catch {
		return false;
	}
}

/**
 * Spawn a detached `pi` process driving the long loop autonomously, with its
 * `--mode json` event stream redirected straight to a journal file. Returns
 * immediately; the caller does not wait for the run to finish.
 */
export function startLongLoopProcess(opts: {
	sessionFolder: string;
	task: string;
	topic: string;
	model?: string;
	cwd: string;
}): LongLoopStatus {
	const { sessionFolder, task, topic, model, cwd } = opts;

	const journalPath = path.join(sessionFolder, "long-loop-journal.jsonl");
	const stderrPath = path.join(sessionFolder, "long-loop-stderr.log");
	const journalFd = fs.openSync(journalPath, "a");
	const stderrFd = fs.openSync(stderrPath, "a");

	const args = ["--mode", "json", "-p", "--approve", "--session-dir", sessionFolder, "--name", `long-loop-${topic}`.slice(0, 80)];
	if (model) args.push("--model", model);
	args.push(task);

	const invocation = getPiInvocation(args);
	const proc = spawn(invocation.command, invocation.args, {
		cwd,
		shell: false,
		detached: true,
		stdio: ["ignore", journalFd, stderrFd],
	});
	proc.unref();
	fs.closeSync(journalFd);
	fs.closeSync(stderrFd);

	const status: LongLoopStatus = {
		pid: proc.pid!,
		topic,
		sessionFolder,
		journalPath,
		stderrPath,
		model,
		startedAt: new Date().toISOString(),
	};
	writeStatus(status);
	return status;
}

export interface JournalEvent {
	type: string;
	toolName?: string;
	message?: { role?: string; content?: unknown };
}

/** Best-effort tail parse of the journal's JSONL events. Malformed lines are skipped. */
export function readJournalTail(journalPath: string, maxLines = 4000): JournalEvent[] {
	let text: string;
	try {
		text = fs.readFileSync(journalPath, "utf-8");
	} catch {
		return [];
	}
	const lines = text.split("\n").filter(Boolean).slice(-maxLines);
	const events: JournalEvent[] = [];
	for (const line of lines) {
		try {
			events.push(JSON.parse(line));
		} catch {
			// skip malformed/partial lines
		}
	}
	return events;
}

export function journalLastModified(journalPath: string): Date | null {
	try {
		return fs.statSync(journalPath).mtime;
	} catch {
		return null;
	}
}

/** Extract the most recent tool calls and assistant text snippets, most-recent last. */
export function summarizeJournal(events: JournalEvent[], maxItems = 10): string[] {
	const items: string[] = [];
	for (const event of events) {
		if (event.type === "tool_execution_start" && event.toolName) {
			items.push(`tool: ${event.toolName}`);
		} else if (event.type === "message_end" && event.message?.role === "assistant") {
			const content = event.message.content;
			if (Array.isArray(content)) {
				for (const part of content as Array<{ type?: string; text?: string }>) {
					if (part?.type === "text" && part.text) items.push(`text: ${part.text.slice(0, 200)}`);
				}
			}
		}
	}
	return items.slice(-maxItems);
}

/** Scan every markdown file directly under sessionFolder for the long-loop ESCALATE: contract. */
export function scanEscalations(sessionFolder: string): Array<{ file: string; line: string }> {
	const results: Array<{ file: string; line: string }> = [];
	let entries: fs.Dirent[];
	try {
		entries = fs.readdirSync(sessionFolder, { withFileTypes: true });
	} catch {
		return results;
	}
	for (const entry of entries) {
		if (!entry.isFile() || !entry.name.endsWith(".md")) continue;
		const fullPath = path.join(sessionFolder, entry.name);
		let content: string;
		try {
			content = fs.readFileSync(fullPath, "utf-8");
		} catch {
			continue;
		}
		for (const line of content.split("\n")) {
			if (line.includes("ESCALATE:")) results.push({ file: entry.name, line: line.trim() });
		}
	}
	return results;
}
