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
3. apply the forward-backward method: work backward from the desired green (passing) outcome and forward from the current red (failing) state. See `developer/references/forward_backward.md`. Note: for thinking skills, the map can be part of the file in the `thinking/<problem-slug>.md` file, rather than in the `maps/` directory.
4. Produce a thinking doc.
5. Return control to `developer:red-green-refactor` with a pointer to the thinking doc.

## Thinking Doc Format

Save to `.ailly/developer/YYYY-MM-DD-A-<topic>/thinking/<problem-slug>.md`:

```markdown
# Thinking: <problem-slug>

**Error:** `<exact error message>`

**Context:** <what plan step was being implemented>

## Situation Summary

<2-3 sentences describing what was being attempted and where it broke>

## Root Cause Analysis

<What is actually wrong. Be specific: wrong type, missing import, API misuse, incorrect assumption about the library, etc.>

## Forward-Backward Map <if more than two steps>

<A forward-backward map for how the steps below were identified.>

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
- May use codemode or equivalent to explore APIs, creating scripts in a `tmp` folder and executing them or sending scripts to a repl.
- May NOT edit project files, run project scripts, or invoke implementation skills

## Return

After writing the thinking doc, return to the caller with:

> "Thinking complete. Root cause: `<one sentence>`. Next steps in `.ailly/developer/YYYY-MM-DD-A-<topic>/thinking/<problem-slug>.md`."
