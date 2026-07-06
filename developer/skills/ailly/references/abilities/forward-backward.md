---
title: Forward/Backward Method for Algorithms
summary: "The Forward/Backward method is a pattern for developing a plan to get from a starting point to an ending point through unknown intermediate challenges. The technique relies on asking two key questions: what information can be immediately derived from forward steps, and what information would lead to backward steps?"
---

The forward-backward technique is a pattern for developing a plan to get from "here" to "there." It starts by having a known starting point and an expected ending point. If this is a short distance, that's not a substantial problem, and can probably be done without much of a plan. But as the distance increases, and the terrain or challenges between those points grows, it becomes much more likely to get lost or stuck if you just start going in a straight line.

A direct walk aims towards the goal, takes an appropriately sized step forward, and tries again. If there's terrain or challenges in the way, it might noe be possible to take the next step directly towards the goal. Still, it should be in a direction that continues making progress. This approach is great when the terrain is relatively flat or there are few challenges along the way. But if there's a chasm or impossible gap to traverse, the course is likely to meander very far afield.

The forward-backward method changes this during the planning phase. Instead of only going from the starting point towards the destination, it brainstorms several possible steps that would _end_ at the destination point. Note these down, and then possibly do this again for the two or three best candidates that are "closer" to the starting point. Now there's a wider map of possible places to get to, since getting to any of those steps means there's a known path to the ending point.

Looking at the starting point, brainstorm another several possible steps forward, and choose the two or three of these closest to the destination pieces. Continue this process, going back and forth asking "Where can you go from here?" on the forward side, and "How can you get to here?" on the backward side. Doing this process builds a conceptual map between the starting and ending points. Even if the most likely candidate path doesn't work out in the end, this map already has explored around that path to try a new plan.

## The two key questions

The forward/backward method is explicitly answering these questions to find each step.

- **Forward key question** "What information can you immediately derive or generate from what you already have?"
- **Backward key question** "What are the immediate precursors, information that directly leads to this step?"

These questions have different characters. The forward question is generative, asking what follows naturally. The backward question is diagnostic. it asks what would need to be true just before this step. Applying them alternately is what builds a useful map, rather than a single speculative path.

## Choosing which side to extend

At each iteration, choose which frontier to extend based on which side currently has fewer unexplored branches or where the terrain looks simpler. The goal is to keep both frontiers at roughly the same conceptual depth. A deep frontier on one side and a shallow frontier on the other means the plan is one-sided. Asymmetric expansion frequently signals that one side has hit an implicit constraint that remains unaddressed rather than resolved.

## Written record is not optional

Write each step down as you generate it, not holding it in working memory. The value of the method comes from accumulating a map, not from tracking a single candidate path. For an LLM agent, this means externalizing steps to a file or scratchpad before continuing. A step held only in context can drift or be silently dropped; a written step can be read back and evaluated precisely.

> Follow project conventions for where to put this map. In projects using the developer: skills, it should go in `.ailly/developer/YYYY-MM-DD-A-<topic>/maps/<path>.md`.

## Convergence and failure modes

If, after 6 or 7 iterations, the points line up, you've found a plausible path from the starting to the ending point, and you can record that as the plan to take. The steps are already there, and you can focus on expanding those steps more fully.

If there's still not a clear path after 8 or 9 steps, one of two things might be happening. First, the points might be too far apart. Stop making this plan, record the map thus far, and suggest creating a plan that instead starts over from intermediate points on this map. Second, if the points seem close together and the steps have gotten small or are going orthogonal to the main path, this is a signal of an unpassable chasm. Stop this plan and suggest a new plan exploring the contours of the chasm. There might be a hidden path, or some place to build a bridge, or it may be worth choosing a different ending point entirely.

A third failure mode can appear earlier: the two frontiers keep expanding without growing coming closer. This frequently means the problem statement itself needs sufficient specification, and the starting point or ending point (or both) is a region rather than a single point. Before continuing, check whether the goal is crisp enough to reason backward from, and whether the starting place is fully known. Vague goals produce backward steps that are themselves vague, which cannot connect to forward steps that are concrete. In this situation, rather than starting a new forward/backward exploration, it's better to switch to brainstorming around either the starting point or the ending point (or both).

## Examples

### Test-driven development

Red-Green-Refactor is forward-backward planning applied to code. Writing a failing test first is a backward step: it defines the goal state (a specific behavior that must be true) without specifying how to reach it. The implementation is the forward step. Starting from current code, what minimum change closes the gap between the current failing state and the desired passing state? Refactoring then becomes safe because the backward constraint (the test) remains fixed while you improve the forward path.

The "chasm" in TDD appears when no simple implementation can make a test pass without also requiring changes to untested infrastructure. The signal is a test that requires more than one commit to turn green. This is the cue to decompose: introduce an intermediate point (a smaller, more targeted test) and plan two forward-backward sessions instead of one.

### Debugging

A bug is a known bad output with an unknown cause. Debugging is inherently backward: work from the observed wrong state backward toward the first state that diverged from expectation. Each backward step asks "what would have to be true just before this for this to happen?" until the chain reaches a code path that is reachable from the current codebase. The forward direction then asks "does this path actually get triggered under the conditions that cause the bug?" When the two meet, the root cause is the forward-reachable path that produces the wrong intermediate state.

### Migrating a legacy system

Given a current architecture as start and a target architecture as goal, the direct-walk failure mode is well-known. Incremental changes accumulate technical debt and the codebase spends months in an inconsistent intermediate state. Forward-backward planning works better: backward from the target, identify what interfaces must exist for the target to be achievable. Forward from current, identify what you can extract or isolate without breaking anything. The meeting point is a stable intermediate architecture—a seam—that you can reach from current code and from which you can straightforwardly reach the target. Plan that seam as its own milestone, not as an invisible waypoint.