/**
 * Ailly session-folder resolution, shared by the quick-loop and long-loop
 * drivers (and reusable by anything else that needs a deterministic
 * `.ailly/developer/YYYY-MM-DD-<letter>-<topic>/` folder).
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { nextDatedSlug, slugify, todayIso } from "./subprocess.ts";

export async function resolveAillySessionFolder(cwd: string, topic: string, given?: string): Promise<string> {
	if (given) {
		const resolved = path.resolve(cwd, given);
		await fs.promises.mkdir(resolved, { recursive: true });
		return resolved;
	}
	const parentDir = path.join(cwd, ".ailly", "developer");
	await fs.promises.mkdir(parentDir, { recursive: true });
	const dirName = nextDatedSlug(parentDir, todayIso(), slugify(topic));
	const resolved = path.join(parentDir, dirName);
	await fs.promises.mkdir(resolved, { recursive: true });
	return resolved;
}

/** All `.ailly/developer/*` session directories directly under cwd. */
export function listAillySessionDirs(cwd: string): string[] {
	const parentDir = path.join(cwd, ".ailly", "developer");
	if (!fs.existsSync(parentDir)) return [];
	return fs
		.readdirSync(parentDir, { withFileTypes: true })
		.filter((e) => e.isDirectory())
		.map((e) => path.join(parentDir, e.name));
}
