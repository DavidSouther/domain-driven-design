# Persuasion in skill design

## Overview

LLMs respond to persuasion the same way humans do.
This helps you design better skills that make important practices work under pressure—honestly, not through trickery.

**Research foundation:** meincke et al. (2025) tested 7 persuasion principles with N=28,000 AI conversations.
Persuasion techniques more than doubled compliance rates (33% → 72%, p < .001).

## The seven principles

### 1. Authority
**What it is:** respect for expertise, credentials, or official sources.

**How it works in skills:**
- Imperative language: "YOU MUST," "Never," "Always"
- Non-negotiable framing: "No exceptions"
- Removes decision fatigue and excuses

**When to use:**
- Discipline-enforcing skills (TDD, verification requirements)
- Safety-critical practices
- Established best practices

**Example:**
```markdown
✅ Write code before test? Delete it. Start over. No exceptions.
❌ Consider writing tests first when feasible.
```

### 2. Commitment
**What it is:** following through on what you've said or done before.

**How it works in skills:**
- Require announcements: "Announce skill usage"
- Force explicit choices: "Choose A, B, or C"
- Use tracking: TodoWrite for checklists

**When to use:**
- Ensuring skills are actually followed
- Multi-step processes
- Accountability mechanisms

**Example:**
```markdown
✅ When you find a skill, you MUST announce: "I'm using [Skill Name]"
❌ Consider letting your partner know which skill you're using.
```

### 3. Scarcity
**What it is:** urgency from time limits or limited availability.

**How it works in skills:**
- Time-bound requirements: "Before proceeding"
- Required order: "Immediately after X"
- Prevents procrastination

**When to use:**
- Immediate verification requirements
- Time-sensitive workflows
- Preventing "I'll do it later"

**Example:**
```markdown
✅ After completing a task, IMMEDIATELY request code review before proceeding.
❌ You can review code when convenient.
```

### 4. Social proof
**What it is:** doing what others do or what's normal.

**How it works in skills:**
- Universal patterns: "Every time," "Always"
- What fails: "X without Y = failure"
- Establishes norms

**When to use:**
- Documenting universal practices
- Warning about common failures
- Reinforcing standards

**Example:**
```markdown
✅ Checklists without TodoWrite tracking = steps get skipped. Every time.
❌ Some people find TodoWrite helpful for checklists.
```

### 5. Unity
**What it is:** being part of a group with shared goals.

**How it works in skills:**
- Collaborative language: "this codebase," "colleagues working together"
- Shared goals: "colleagues both want quality"

**When to use:**
- Collaborative workflows
- Establishing team culture
- Non-hierarchical practices

**Example:**
```markdown
✅ Colleagues working together. Your honest technical judgment is needed.
❌ You should probably tell if something's wrong.
```

### 6. Reciprocity
**What it is:** obligation to return benefits received.

**How it works:**
- Use sparingly - can feel manipulative
- Rarely needed in skills

**When to avoid:**
- Almost always (other principles more effective)

### 7. Liking
**What it is:** preference for cooperating with those one likes.

**How it works:**
- **DON'T USE for compliance**
- Conflicts with honest feedback culture
- Creates false flattery

**When to avoid:**
- Always for discipline enforcement

## Principle combinations by skill type

| Skill Type | Use | Avoid |
|------------|-----|-------|
| Discipline-enforcing | Authority + Commitment + Social Proof | Liking, Reciprocity |
| Guidance/technique | Moderate Authority + Unity | Heavy authority |
| Collaborative | Unity + Commitment | Authority, Liking |
| Reference | Clarity only | All persuasion |

## Why this works: the psychology

**Clear rules reduce excuses:**
- "YOU MUST" removes decision fatigue
- Absolute language eliminates "is this an exception?"
  questions
- Direct language blocks common workarounds

**Implementation intentions create automatic behavior:**
- Clear triggers + required actions = automatic execution
- "When X, do Y" more effective than "generally do Y"
- Reduces thinking required for compliance

**LLMs learn from human patterns:**
- They're trained on human text containing these patterns
- Authority language connects to compliance in training data
- Commitment sequences (statement → action) appear often
- Social proof patterns (everyone does X) establish norms

## Ethical use

**Legitimate:**
- Ensuring people implement critical practices
- Creating effective documentation
- Preventing predictable failures

**Illegitimate:**
- Manipulating for personal gain
- Creating false urgency
- Guilt-based compliance

**The test:** would this technique serve the user's genuine interests if they fully understood it?

## Research citations

**Cialdini, R. B. (2021).**
*Influence: the psychology of persuasion (New and Expanded).*
Harper Business.
- Seven principles of persuasion
- Empirical foundation for influence research

**Meincke, L., Shapiro, D., Duckworth, A. L., Mollick, E., Mollick, L., & Cialdini, R. (2025).**
"Call me a jerk: persuading AI to comply with objectionable requests."
University of Pennsylvania.
- Tested 7 principles with N=28,000 LLM conversations
- Compliance increased 33% → 72% with persuasion techniques
- Authority, commitment, scarcity most effective
- Shows that LLMs respond like humans to these techniques

## Quick reference

When designing a skill, ask:

1. **What type is it?**
   (Discipline vs. guidance vs. reference)
2. **What behavior should change?**
3. **Which principles apply?**
   In most cases authority and commitment for discipline.
4. **Are too many combined?**
   (Don't use all seven)
5. **Is this ethical?**
   (Serves user's genuine interests?)
