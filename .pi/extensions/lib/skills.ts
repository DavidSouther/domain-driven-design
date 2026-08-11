/**
 * Skill-name resolution, mirroring pi's own discovery precedence.
 *
 * `review_run`'s `specialists` parameter names a skill the way pi itself
 * knows it — by frontmatter `name`, not by a directory convention this
 * package invents. That is what makes "a newly installed specialist is
 * composed in with no edit here" (general:review's own words) actually true
 * for pi: a project using this package can add its own brand-new specialist
 * skill under its own `.pi/skills/` or `.agents/skills/`, or get one from a
 * *different* installed pi package, and name it here with zero changes to
 * this extension or to general/skills/review/SKILL.md.
 *
 * This resolves by walking the same locations pi's own resource loader
 * checks, project scope before package scope before global scope, so a
 * project-local override of a same-named specialist wins the way it would
 * for pi's own skill discovery.
 */

import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { loadSkillsFromDir } from "@earendil-works/pi-coding-agent";

/** This package's own plugin skill directories, relative to its repo root. */
export const PACKAGE_SKILL_DIRS = [
	"developer/skills",
	"general/skills",
	"domain/skills",
	"patterns/skills",
	"research/skills",
];

function findProjectSkillDirs(cwd: string): string[] {
	const dirs: string[] = [];
	let dir = path.resolve(cwd);
	while (true) {
		for (const name of [".pi/skills", ".agents/skills"]) {
			const candidate = path.join(dir, name);
			if (fs.existsSync(candidate)) dirs.push(candidate);
		}
		if (fs.existsSync(path.join(dir, ".git"))) break;
		const parent = path.dirname(dir);
		if (parent === dir) break;
		dir = parent;
	}
	return dirs;
}

function globalSkillDirs(): string[] {
	const home = os.homedir();
	return [path.join(home, ".pi", "agent", "skills"), path.join(home, ".agents", "skills")];
}

/**
 * A caller-facing specialist id may still carry the "<plugin>:<skill>"
 * habit from this repository's cross-harness prose (Claude Code's
 * plugin-qualified skill invocation). Pi has no such namespace — skill
 * `name` is unique on its own — so only the trailing segment is meaningful.
 */
export function specialistSkillName(specialist: string): string {
	const idx = specialist.lastIndexOf(":");
	return idx === -1 ? specialist : specialist.slice(idx + 1);
}

/**
 * Resolve a skill name to its `SKILL.md` absolute path, checking (in
 * precedence order): the current project's own `.pi/skills`/`.agents/skills`
 * at every directory from `cwd` up to its repo root, then this package's own
 * plugin skill directories, then the user-global skill directories. Returns
 * `null` if no loaded location has a skill by that name.
 */
export function findSkillByName(name: string, packageRoot: string, cwd: string): string | null {
	const searchDirs = [
		...findProjectSkillDirs(cwd),
		...PACKAGE_SKILL_DIRS.map((d) => path.join(packageRoot, d)),
		...globalSkillDirs(),
	];
	for (const dir of searchDirs) {
		const { skills } = loadSkillsFromDir({ dir, source: "path" });
		const match = skills.find((s) => s.name === name);
		if (match) return match.filePath;
	}
	return null;
}
