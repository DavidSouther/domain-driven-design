/**
 * Ailly Long Loop
 *
 * Models developer/skills/ailly/references/shapes/long-loop.md as a
 * dedicated pi workflow. Long loop is fundamentally different from quick
 * loop: it runs autonomously at project scale, potentially for hours, with
 * a research-and-decide reviewer clearing each draft gate instead of a
 * human. Holding one synchronous tool call open for that long blocks the
 * interactive session with no way to interject, and loses everything on a
 * transient error. So this models it as three tools plus a background
 * watcher instead of one big call:
 *
 * - `ailly_long_loop_start` spawns the loop as a **detached background pi
 *   process** — a real second agent, with its own session file colocated in
 *   the session folder, given the same ailly_subagent/review_run tools this
 *   package provides — and returns immediately. Its `--mode json` event
 *   stream is redirected straight to a journal file; nothing about status
 *   reporting trusts the background run's self-report.
 * - `ailly_long_loop_status` reads that journal and a small status header
 *   back deterministically: process liveness, staleness (no journal growth
 *   in the last several minutes), and a scan for the long-loop reviewer
 *   contract's own `ESCALATE:` markers across the session folder's artifacts.
 * - `ailly_long_loop_stop` ends it.
 * - A `session_start`-registered background watcher is the "background LLM
 *   steering" piece: every few minutes it checks every long loop running
 *   under the current project, and when one goes stale, escalates, or exits,
 *   it notifies and injects a follow-up message into the *live* interactive
 *   session so the foreground model picks it up and can decide whether to
 *   intervene — without the human having to remember to poll status by hand.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import {
	isPidAlive,
	journalLastModified,
	readJournalTail,
	readStatus,
	scanEscalations,
	startLongLoopProcess,
	summarizeJournal,
	writeStatus,
} from "../lib/long-loop.ts";
import { resolveAillySessionFolder, listAillySessionDirs } from "../lib/session.ts";

const STALE_MINUTES = 10;
const WATCH_INTERVAL_MS = 3 * 60 * 1000;

function buildLongLoopTask(topic: string, sessionFolder: string): string {
	return [
		`Read developer/skills/ailly/SKILL.md, developer/skills/ailly/references/shapes/long-loop.md,`,
		`and developer/skills/ailly/references/agents/pi.md.`,
		`Run the long loop, exactly as those three documents specify, for topic "${topic}" at session folder ${sessionFolder}.`,
		`Dispatch every phase through the ailly_subagent tool, one reference at a time. Review every artifact through the`,
		`review_run tool. At each draft gate, dispatch a fresh research-and-decide reviewer per long-loop.md section 2`,
		`(use ailly_subagent's thinking/intent-review reference, or run the reviewer contract inline if no closer match`,
		`applies) to resolve open items and clear the gate, escalating per the three triggers in section 4 rather than`,
		`guessing. The human merge gate and the Closing Bell are never auto-cleared by any reviewer — stop there and wait.`,
		`When you stop, your final message must be the end-of-run report from long-loop.md section 7.`,
	].join(" ");
}

const StartParams = Type.Object({
	topic: Type.String({ description: "Short topic/feature description for the session folder slug and the run's task." }),
	sessionFolder: Type.Optional(Type.String({ description: "Resume an existing session folder instead of creating a new one." })),
	model: Type.Optional(Type.String({ description: "Model id/pattern the background long-loop process runs with." })),
});

const SessionFolderParams = Type.Object({
	sessionFolder: Type.String({ description: "The session folder a prior ailly_long_loop_start call returned." }),
});

const StopParams = Type.Object({
	sessionFolder: Type.String({ description: "The session folder a prior ailly_long_loop_start call returned." }),
	reason: Type.Optional(Type.String({ description: "Why the loop is being stopped, recorded in its status file." })),
});

function statusReport(sessionFolder: string): string {
	const status = readStatus(sessionFolder);
	if (!status) return `No long-loop status found at ${sessionFolder}.`;
	const alive = !status.stopped && isPidAlive(status.pid);
	const lastModified = journalLastModified(status.journalPath);
	const staleMinutes = lastModified ? (Date.now() - lastModified.getTime()) / 60000 : null;
	const events = readJournalTail(status.journalPath);
	const recent = summarizeJournal(events);
	const escalations = scanEscalations(status.sessionFolder);

	const lines = [
		`Long loop: ${status.topic}`,
		`Session folder: ${status.sessionFolder}`,
		`PID ${status.pid} — ${status.stopped ? `stopped (${status.stopReason ?? "no reason given"})` : alive ? "running" : "not running (process exited)"}`,
		`Started: ${status.startedAt}`,
		staleMinutes !== null ? `Journal last updated: ${staleMinutes.toFixed(1)} min ago${staleMinutes > STALE_MINUTES ? " — STALE" : ""}` : "Journal: no activity recorded yet",
		`Recent activity (${recent.length} items):`,
		...recent.map((r) => `  - ${r}`),
		escalations.length > 0
			? `ESCALATE markers found (${escalations.length}):\n` + escalations.map((e) => `  - ${e.file}: ${e.line}`).join("\n")
			: "No ESCALATE markers found.",
	];
	return lines.join("\n");
}

export default function (pi: ExtensionAPI) {
	let currentCtx: ExtensionContext | undefined;
	let watchInterval: ReturnType<typeof setInterval> | undefined;
	const notifiedDone = new Set<string>();
	const notifiedStale = new Set<string>();
	const notifiedEscalations = new Set<string>();

	function steer(message: string) {
		if (currentCtx?.hasUI) currentCtx.ui.notify(message, "info");
		pi.sendMessage(
			{ customType: "ailly-long-loop", content: message, display: true },
			{ deliverAs: "followUp" },
		);
	}

	function watchTick(cwd: string) {
		for (const sessionFolder of listAillySessionDirs(cwd)) {
			const status = readStatus(sessionFolder);
			if (!status || status.stopped) continue;

			const alive = isPidAlive(status.pid);
			if (!alive) {
				if (!notifiedDone.has(sessionFolder)) {
					notifiedDone.add(sessionFolder);
					steer(`Long loop "${status.topic}" is no longer running (pid ${status.pid} exited). Check ${sessionFolder} — it may have finished, hit the merge gate, or crashed. Run ailly_long_loop_status to see the end-of-run report.`);
				}
				continue;
			}

			const lastModified = journalLastModified(status.journalPath);
			const staleMinutes = lastModified ? (Date.now() - lastModified.getTime()) / 60000 : 0;
			if (staleMinutes > STALE_MINUTES) {
				if (!notifiedStale.has(sessionFolder)) {
					notifiedStale.add(sessionFolder);
					steer(`Long loop "${status.topic}" has produced no activity for ${staleMinutes.toFixed(0)} minutes but is still running (pid ${status.pid}). It may be stuck. Check ${sessionFolder}/long-loop-journal.jsonl, or ailly_long_loop_stop it.`);
				}
			} else {
				notifiedStale.delete(sessionFolder);
			}

			for (const escalation of scanEscalations(sessionFolder)) {
				const key = `${sessionFolder}|${escalation.file}|${escalation.line}`;
				if (notifiedEscalations.has(key)) continue;
				notifiedEscalations.add(key);
				steer(`Long loop "${status.topic}" recorded an escalation in ${escalation.file}: ${escalation.line}\nIt will hold that gate for a human. Check ${sessionFolder}.`);
			}
		}
	}

	pi.on("session_start", async (_event, ctx) => {
		currentCtx = ctx;
		if (watchInterval) clearInterval(watchInterval);
		watchInterval = setInterval(() => watchTick(ctx.cwd), WATCH_INTERVAL_MS);
	});

	pi.on("session_shutdown", async () => {
		if (watchInterval) {
			clearInterval(watchInterval);
			watchInterval = undefined;
		}
	});

	pi.registerTool({
		name: "ailly_long_loop_start",
		label: "Ailly Long Loop Start",
		description: [
			"Start developer:ailly's long loop as a detached background process:",
			"runs all five phases autonomously, using a research-and-decide reviewer",
			"to clear each draft gate instead of a human, stopping only at the human",
			"merge gate or the Closing Bell. Returns immediately — use",
			"ailly_long_loop_status to check progress and ailly_long_loop_stop to end",
			"it. A background watcher also nudges this session when the loop stalls,",
			"escalates, or exits. Only for work the long loop is meant for: ambiguous,",
			"high-blast-radius, or security-sensitive work quick-loop is forbidden",
			"from, where you still want full-fidelity artifacts and deliberation.",
		].join(" "),
		parameters: StartParams,
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			const sessionFolder = await resolveAillySessionFolder(ctx.cwd, params.topic, params.sessionFolder);
			const existing = readStatus(sessionFolder);
			if (existing && !existing.stopped && isPidAlive(existing.pid)) {
				return {
					content: [{ type: "text", text: `A long loop is already running at ${sessionFolder} (pid ${existing.pid}). Use ailly_long_loop_status or ailly_long_loop_stop first.` }],
					isError: true,
					details: existing,
				};
			}

			const task = buildLongLoopTask(params.topic, sessionFolder);
			const status = startLongLoopProcess({ sessionFolder, task, topic: params.topic, model: params.model, cwd: ctx.cwd });
			notifiedDone.delete(sessionFolder);
			notifiedStale.delete(sessionFolder);

			return {
				content: [
					{
						type: "text",
						text: [
							`Long loop started in the background.`,
							`Session folder: ${sessionFolder}`,
							`PID: ${status.pid}`,
							`Journal: ${status.journalPath}`,
							`This does not block — check ailly_long_loop_status(sessionFolder) for progress. The human merge gate and the Closing Bell are never auto-cleared; this session will also be nudged automatically if the loop stalls, escalates, or exits.`,
						].join("\n"),
					},
				],
				details: status,
			};
		},
	});

	pi.registerTool({
		name: "ailly_long_loop_status",
		label: "Ailly Long Loop Status",
		description: "Report a long loop's progress: process liveness, staleness, recent journal activity, and any ESCALATE: markers found in its session folder's artifacts.",
		parameters: SessionFolderParams,
		async execute(_toolCallId, params) {
			return { content: [{ type: "text", text: statusReport(params.sessionFolder) }], details: readStatus(params.sessionFolder) };
		},
	});

	pi.registerTool({
		name: "ailly_long_loop_stop",
		label: "Ailly Long Loop Stop",
		description: "Stop a running long loop's background process.",
		parameters: StopParams,
		async execute(_toolCallId, params) {
			const status = readStatus(params.sessionFolder);
			if (!status) {
				return { content: [{ type: "text", text: `No long-loop status found at ${params.sessionFolder}.` }], isError: true, details: {} };
			}
			let killed = false;
			if (isPidAlive(status.pid)) {
				try {
					process.kill(status.pid, "SIGTERM");
					killed = true;
				} catch (err) {
					return { content: [{ type: "text", text: `Failed to stop pid ${status.pid}: ${(err as Error).message}` }], isError: true, details: status };
				}
			}
			writeStatus({ ...status, stopped: true, stoppedAt: new Date().toISOString(), stopReason: params.reason ?? "stopped by user" });
			return {
				content: [{ type: "text", text: killed ? `Stopped long loop (pid ${status.pid}).` : `Long loop process was already not running; marked stopped.` }],
				details: readStatus(params.sessionFolder),
			};
		},
	});
}
