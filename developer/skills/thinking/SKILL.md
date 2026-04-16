---
name: thinking
description: Use when facing a compiler error, failing test, invalid lint, or other "red" response during coding implementation.
---

# developer:thinking

## Overview

Fresh-context subagent for stuck moments during `developer:red-green-refactor`. Always runs as a subagent. Investigates the problem, produces a concrete next-steps plan, and returns control without modifying any files.

**This skill MUST be invoked as a subagent** via the Agent tool. It does not run inline.

**Hard constraints:**
- Do NOT edit any files
- Do NOT run any code or build commands
- Do NOT propose "try X and see what happens" — every proposed step must have a specific predicted outcome

## Inputs (from red-green-refactor)

The invoking skill must pass:
1. The exact error message (copy-pasted, not paraphrased)
2. The code added or changed in this step (the diff or the relevant snippet)
3. The plan step being implemented (name and description)

## Behavior

1. Read the inputs without editorializing.
2. Use `research:` skills to investigate the problem if needed (e.g., API docs, similar patterns in the codebase, error message semantics).
3. Produce a thinking doc.
4. Return control to `developer:red-green-refactor` with a pointer to the thinking doc.

## Thinking Doc Format

Save to `docs/developer/YYYY-MM-DD-<topic>/thinking/<problem-slug>.md`:

```markdown
# Thinking: <problem-slug>

**Error:** `<exact error message>`

**Context:** <what plan step was being implemented>

## Situation Summary

<2-3 sentences describing what was being attempted and where it broke>

## Root Cause Analysis

<What is actually wrong. Be specific: wrong type, missing import, API misuse, incorrect assumption about the library, etc.>

## Next Steps (in order)

1. **<Specific change>** — expected outcome: `<what the error or test result should look like after this change>`
2. **<Specific change>** — expected outcome: `<what changes next>`
3. ...
```

The next steps must be concrete and ordered. "Try X" without a predicted outcome is not acceptable.

## Scope

- May read files using the Read, Grep, and Glob tools
- May use `research:` skills (research:codebase, research:public, research:dependencies)
- May read documentation and external sources with WebFetch
- May NOT edit files, run code, or invoke implementation skills

## Return

After writing the thinking doc, return to the caller with:

> "Thinking complete. Root cause: `<one sentence>`. Next steps in `docs/developer/YYYY-MM-DD-<topic>/thinking/<problem-slug>.md`."
