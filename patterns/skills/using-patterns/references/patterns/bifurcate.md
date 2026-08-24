# Bifurcate

## Overview

Bifurcation narrows a defect investigation by **splitting the remaining candidate space** with one discriminating test or probe. It asks which large set of explanations a single observation can **rule out**, rather than which fix to try first, carving the space of possible causes into a part the evidence refutes and a part that survives.

Use it after a defect is observed and several plausible causes remain. It is almost the inverse of triangulation: triangulation adds a second **example** to locate a **general implementation**; bifurcation adds a **discriminating observation** to shrink a **hypothesis set**.

## When to Use

- Several plausible causes remain and obvious guesses have not panned out.
- The defect could live in either of two subsystems, code paths, or parameter regions, and the next test should isolate substantial portions of the system.
- You are stepping through code linearly without a predicted outcome for each branch.
- `git bisect` is not enough — the defect may be in logic at the current checkout, not in which commit introduced it.

**When NOT to use:**
- A hardcoded fake passes the first test and you need a second example to force the real implementation — use Triangulate instead.
- Only one plausible cause remains — investigate that cause directly.
- The correct implementation is already obvious — implement it; do not manufacture probes.
- You need to structure a single test's setup/action/assert phases — use Arrange-Act-Assert instead.

## Core Pattern

**Step 1 — Enumerate live hypotheses.** List the explanations still consistent with everything observed so far. Be explicit; a vague "something in the stack" is not a partition.

**Step 2 — Design one bifurcating probe.** Pick a test, direct call, flag toggle, or checkpoint whose **predicted outcomes** map to two non-overlapping groups of hypotheses. Aim for roughly equal information gain — "half" is a guideline, not a strict count.

**Step 3 — Observe and refute.** Run the probe. The outcome is evidence against every hypothesis it contradicts, and those are refuted. Do not reinterpret a contradicting result to keep a favored explanation alive.

**Step 4 — Repeat on the survivor.** Bifurcate again inside the surviving partition until one cause remains or the next step is a direct fix.

### Checkpointing a short linear function

`cpuTick` in the nand2tetris web IDE simulator (`davidsouther/web-ide`, `simulator/src/cpu/cpu.ts`) reaches its result in four statements:

```ts
export function cpuTick(
  { inM, instruction }: CPUInput,
  { A, D, PC }: CPUState
): [CPUState, boolean] {
  const bits = decode(instruction);
  const a = bits.am ? inM : A;
  const [ALU, flag] = alu(bits.op, D, a);

  return [{ A, D, PC: PC + 1, ALU, flag }, bits.d3];
}
```

A wrong `ALU` value has three candidate sources: `decode` extracting the wrong `op` or `am` bit, the `a` mux selecting the wrong operand, or `alu` miscomputing. Checkpoint the midpoint rather than reading all three:

```ts
const bits = decode(instruction);
expect(bits.op).toBe(0b000010); // D+A
expect(bits.am ? inM : A).toBe(expectedOperand);
```

Holding refutes `decode` and the mux, leaving `alu` as the surviving candidate. Failing refutes `alu` as the cause of *this* observation; the surviving partition is still `decode` or the mux, so the next probe splits those two.

### Choosing an input that represents part of the space

`alua` in the same simulator (`simulator/src/cpu/alu.ts`) takes a six-bit control word, where the four high bits preprocess the operands and the two low bits select the operation and post-negate:

```ts
export function alua(op: number, d: number, a: number): [number, number] {
  if (op & 0b100000) d = 0;
  if (op & 0b010000) d = ~d & 0xffff;
  if (op & 0b001000) a = 0;
  if (op & 0b000100) a = ~a & 0xffff;

  let o = (op & 0b000010 ? d + a : d & a) & 0xffff;
  if (op & 0b000001) o = ~o & 0xffff;
  // ... flags and return ...
}
```

Two partitions of the control word: the four high bits (operand preprocessing) versus the two low bits (add versus AND, then post-negate). `op = 0b000010` (`x+y`) leaves every preprocessing bit clear, so those four `if`s do not run.

If that case is wrong, the evidence refutes "the defect is in preprocessing" — those branches never executed — and the surviving partition is add / AND / negate. If that case is right, un-preprocessed addition is refuted as the cause; preprocessing and the AND / negate paths remain live, and the next probe splits them. "Half" is a guideline for information gain, not a claim that one input covers every remaining op.

### Direct call and comment-out

Call the suspect API or function in isolation — success or failure refutes either the routine or the surrounding orchestration. Comment out a subsystem block; if the symptom persists, that block is not the cause.

### Relation to git bisect

`git bisect` bifurcates **across commits** — each good/bad answer halves a revision range. Bifurcation here operates **within one investigation** at a single checkout: subsystems, layers, functions, branches, inputs. Use both when appropriate; bisect finds *when* a defect arrived, bifurcation finds *where* it lives in the current code.

## Quick Reference

| Situation | What to do |
|-----------|------------|
| Two subsystems could explain the defect | Probe one subsystem directly; the outcome refutes one side |
| Long call chain, unknown layer | Comment out or bypass middle layers; observe whether the symptom persists |
| Wide parameter space | Pick an input exercising one region; the result refutes that region or the rest |
| Long procedure, unknown segment | Checkpoint state mid-procedure; pass/fail splits before vs after |
| One hypothesis left | Stop bifurcating; confirm and fix that cause |
| Obvious leads exhausted | Bifurcate before random line-by-line debugging |

## Common Mistakes

- **Probing without a predicted partition.** Running a probe and only then deciding what it meant lets any outcome fit a story. Write the pass/fail interpretations before you run.
- **Degenerate splits.** A probe whose outcomes leave the same candidates either way wastes a cycle — redesign it so each outcome refutes a real portion of the space.
- **Confirming instead of falsifying.** Seeking support for a favored hypothesis rather than evidence against alternatives. Bifurcation asks what is *not* the answer.
- **Treating a refuted hypothesis as still live.** Reinterpreting a contradicting result to keep a preferred cause in play throws away the only information the probe bought.
- **Skipping enumeration.** Without a written hypothesis list, "half" is meaningless and later probes cover ground already refuted.
- **Stopping after one split when several causes remain.** Bifurcation is recursive; repeat on the surviving partition until the space is small enough to fix directly.

## Composes With

- **triangulate (`references/patterns/triangulate.md`)** — inverse pressure: triangulation grows examples to find an implementation; bifurcation refutes hypotheses to find a defect. Triangulate during uncertain green steps; bifurcate when several causes remain after a red test or a production failure.
- **arrange-act-assert (`references/patterns/arrange-act-assert.md`)** — each bifurcating probe is still one test with clear setup, a single action, and an assertion whose outcome carries the partition meaning.
- **developer:thinking (`developer/skills/ailly/references/abilities/thinking.md`)** — when forward/backward analysis leaves multiple live explanations during a stuck build, choose the next step as a bifurcating probe with predicted outcomes per partition.
- **research:archaeology** — `git bisect` is commit-range bifurcation; use archaeology when the question is which change introduced the defect, and bifurcate when the question is where in the current code it lives.

## Additional Notes

Bifurcation shines once obvious leads are exhausted — recent-change guesses, log skimming, reproduction on the happy path. It is deliberately counterintuitive, since the probe is designed to eliminate explanations rather than to produce a fix, but it is cheap relative to open-ended debugging.
