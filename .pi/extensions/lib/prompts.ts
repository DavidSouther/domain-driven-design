/**
 * Loads the prompt templates under ./prompts/, substituting `{{name}}`
 * placeholders. Keeps LLM-facing prose in reviewable markdown instead of
 * string arrays inside the extension code.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const PROMPTS_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), "prompts");

export function loadPrompt(name: string, vars: Record<string, string> = {}): string {
	let text = fs.readFileSync(path.join(PROMPTS_DIR, `${name}.md`), "utf-8");
	for (const [key, value] of Object.entries(vars)) {
		text = text.replaceAll(`{{${key}}}`, value);
	}
	return text.trimEnd();
}
