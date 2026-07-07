---
name: dispatching-agents
description: Use when preparing to start subagents. Especially multiple independent task.
---

# Dispatching agents

## Overview

Delegate tasks to specialized agents with isolated context. Craft their instructions precisely so each agent stays focused on one problem domain without inheriting your session's history. This preserves your own context for coordination work.

When multiple unrelated failures appear across different test files or subsystems, investigating them sequentially wastes time. Each investigation is independent and can happen concurrently.

**Core principle:** one agent per independent problem domain. Let them work concurrently.

## When to use

```dot
digraph when_to_use {
    multiple [shape=diamond label="Multiple failures?"];
    independent [shape=diamond label="Are they independent?"];
    single [shape=box label="Single agent investigates all"];
    parallel_ok [shape=diamond label="Can they work in parallel?"];
    sequential [shape=box label="Sequential agents"];
    parallel [shape=box label="Parallel dispatch"];

    multiple -> independent [label="yes"];
    independent -> single [label="no - related"];
    independent -> parallel_ok [label="yes"];
    parallel_ok -> parallel [label="yes"];
    parallel_ok -> sequential [label="no - shared state"];
}
```

**Use when:**
- Three or more test files failing with different root causes
- Multiple subsystems broken independently
- Each problem remains independent of others
- No shared state between investigations

**When NOT to use:**
- Failures relate to each other. Fixing one might fix others, so investigate them together first.
- Understanding requires seeing the full system state.
- Agents would interfere with each other (editing same files, shared resources).
- The failure scope is not yet known.

## Delegation signals

The first question is whether you should dispatch a sub-step to a subagent. Check these signals before reaching for model-selection guidance.

**Positive signals (favor dispatch):**
- Independent scope with a clear input/output boundary. The step receives a self-contained brief and returns a self-contained result.
- Parallelizable with other work. The step can run concurrently with other sub-steps or with work the caller is doing itself.
- A genuine cost or capability mismatch. The step's complexity profile differs enough from the caller's own that isolating it lets it run on a cheaper or more specialized model.
- A structured, deterministic hand-off. The caller can describe the step once, completely, without needing ongoing back-and-forth.

**Negative signals (favor staying inline):**
- Forced decomposition. The "step" exists only as a named heading in a plan or reference, with no real independent work behind it.
- Tight, low-latency, multi-turn coupling to context the caller already holds in-session. The step needs to keep asking the caller things a subagent would have to reconstruct from scratch.
- Round-trip coordination overhead. An extra model call plus context reconstruction on return would cost more than isolating the step saves.

Dispatch a subagent once one of these signals is real, not because a step happens to have a name.

## The pattern

### 1. Identify independent operations 

Group failures by what broke:
- File A tests: Tool approval flow
- File B tests: Batch completion behavior
- File C tests: Stop capability

Group research by areas
- Internal search for conversations and designs
- Codebase search for existing implementation
- Public search for external context.

Each domain is independent. Fixing tool approval does not affect stop tests.

### 2. Create focused agent tasks

Each agent gets:
- **Specific scope:** One test file or subsystem
- **Clear goal:** Make these tests pass
- **Constraints:** Do not change other code
- **Expected output:** Summary of root cause and what you fixed

### 3. Dispatch in parallel

```typescript
Task("Fix agent-tool-abort.test.ts failures")
Task("Fix batch-completion-behavior.test.ts failures")
Task("Fix tool-approval-race-conditions.test.ts failures")
// All three run concurrently
```

### 4. Review and Integrate

When agents return:
- Read each summary
- Verify fixes do not conflict
- Run full test suite
- Integrate all changes

## Agent prompt structure

Effective agent prompts focus on specific, self-contained goals with clear expected output:

```markdown
Fix the 3 failing tests in src/agents/agent-tool-abort.test.ts:

1. "should abort tool with partial output capture" - expects 'interrupted at' in message
2. "should handle mixed completed and aborted tools" - fast tool aborted instead of completed
3. "should properly track pendingToolCount" - expects 3 results but gets 0

These are timing/race condition issues. Your task:

1. Read the test file and understand what each test verifies
2. Identify root cause - timing issues or actual bugs?
3. Fix by:
   - Replacing arbitrary timeouts with event-based waiting
   - Fixing bugs in abort implementation if found
   - Adjusting test expectations if testing changed behavior

Do NOT just increase timeouts - find the real issue.

Return: Summary of what you found and what you fixed.
```

## Common mistakes

**❌ Too broad:** "Fix all the tests" - agent gets lost.
**✅ Specific:** "Fix agent-tool-stop.test.ts" - focused scope.

**❌ No context:** "Fix the race condition" - agent does not know where to look.
**✅ Context:** paste the error messages and test names.

**❌ No constraints:** agent might refactor unrelated code.
**✅ Constraints:** "do NOT change production code" or "fix tests only."

**❌ Vague output:** "Fix it" - no record of what changed.
**✅ Specific:** "return summary of root cause and changes."

## Verification

After agents return:
1. **Review each summary**: understand what changed and why
2. **Check for conflicts**: Did agents edit the same code?
3. **Run full suite**: verify all fixes work together
4. **Spot check**: agents can make systematic errors; read key diffs
