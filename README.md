# DDD & Design Patterns Skills for Claude Code

A [Claude Code](https://claude.ai/code) plugin providing structured workflows for Domain-Driven Design, software design patterns, research, and a strict test-driven developer lifecycle.

## Installation & Getting Started

1. Add the marketplace from GitHub: in Claude Code, run `/plugin marketplace add davidsouther/domain-driven-design`.
   * You can also run `/plugin` to open the interactive browser and add it from the **Marketplaces** tab.
2. Install the skills with `/plugin install <name>@ailly` — install `general`, `developer`, `patterns`, and `research` (`domain` is optional). Browse and toggle them anytime from the **Installed** tab of `/plugin`.
3. Start a project in a new folder - `/ailly initialize a project called [name] for [design goal] using [TypeScript, Python, or Rust] (including initializing git)`.
4. Start work on a new feature - `/ailly start work on [description]`.
5. Start a feature in an isolated worktree - `/ailly in a worktree start work on [description]`.
6. Continue work on a specific phase - `/ailly continue [phase] [task-slug]`.
7. Fast-track a simple change - `/ailly finish [task] with a quick loop`.
8. Tell Ailly to do research herself - after Ailly asks you a question, `/using-research to perform a deep dive; pay attention especially to [area of interest]`.
9. When finished with a task, `/ailly cleanup [task] with a PR`. Or use `with a squash merge` for local development.

> **Updating:** Ailly does not auto-update when new versions are pushed. Run `/plugin marketplace update ailly` to pull the latest skills.
> **Local development:** To work from a local clone instead, run `/plugin marketplace add <path-to-clone>`.

### How Ailly Works

Ailly structures development as five sequential phases, each running in its own session to prevent context bloat:

| Phase | What happens |
|-------|-------------|
| **Research** | Gathers reference material, produces a refined report with user review |
| **Design** | Produces a design doc with purpose, user journey, spec, and alternatives; outputs a failing feature test |
| **Plan** | Details type-first, TDD implementation steps; user reviews before build begins |
| **Build** | Executes each plan step, runs checks, commits; targets a passing feature test |
| **Cleanup** | Removes session artifacts, squash-merges the branch |

Each phase produces a draft artifact. A human must review and clear the draft marker before the next phase begins — this keeps architectural decisions collaborative rather than delegated entirely to the agent.

The **quick loop** option skips the full phase structure for simple, unambiguous tasks.

### Useful Patterns

- Write a complex task description to `.ailly/prompts/[topic].md`, then run it with `/ailly run .ailly/prompts/[topic].md`.
- Work on multiple independent features at the same time using worktrees: `/ailly in a worktree start work on [feature-a]` in one terminal, the same for feature-b in another.
- Check if Ailly has what she needs for research - `/ailly check if internal, books, and papers research are set up right`.
- Ask Ailly about herself - `/ailly what skills are available?` or `/ailly how do I update a git repo?`
- Change the `.ailly/` folder by adding `For developer: tools, use .agents/ instead of .ailly/` to your AGENTS.md or equivalent.

## Skills

### General (`general:*`)

Utilities for skill authoring, parallel agent dispatch, and git worktree isolation.

| Skill | When to use |
|-------|-------------|
| `general:using-general` | Bootstrap — load before any action to find the most relevant skills |
| `general:using-git-worktrees` | Starting feature work that needs isolation from the current workspace |
| `general:dispatching-parallel-agents` | Multiple independent tasks with no shared state or sequential dependencies |
| `general:writing-skills` | Creating, editing, or verifying skills before deployment |

### Developer (`developer:*`)

A strict three-loop development lifecycle: design → feature test → TDD implementation.

| Skill | When to use |
|-------|-------------|
| `developer:ailly` | Starting or resuming a feature development session. The main driver for development. Running `/ailly` in Claude will get it going on the next thing. |
| `developer:using-developer` | Bootstrap skill that guides which developer skill to invoke for the current situation |
| `developer:initialize` | Setting up a new project or language environment |
| `developer:design` | Formatting or structuring a design doc |
| `developer:feature-test` | Writing the feature test after design is approved |
| `developer:plan` | Breaking a failing feature test into implementation steps |
| `developer:red-green-refactor` | Implementing a plan step with TDD |
| `developer:refactor` | Tests are green; cleaning up code before continuing |
| `developer:think` | Stuck on a compiler error or test failure during TDD |

The developer lifecycle uses draft gates: each artifact (design doc, feature test, plan) must be human-reviewed and cleared before the next loop begins.

### Domain-Driven Design (`domain:*`)

Guides architectural decisions and domain modeling through the full DDD lifecycle.

| Skill | When to use |
|-------|-------------|
| `domain:using-domain` | Bootstrap — establishes when to invoke each DDD skill |
| `domain:arrow-of-maturity` | Evaluating architecture, adding persistence, or feeling scaling pressure |
| `domain:contracts-and-invariants` | Designing API boundaries, service interfaces, or domain operations |
| `domain:domain-model` | Starting a new project, service, or feature with business logic |
| `domain:glossary` | Any ambiguous or potentially synonymous term appears |
| `domain:ubiquitous-language` | Naming entities, operations, or domain concepts |

The Arrow of Maturity describes six architectural stages a DDD project grows through, from prototype scripts to event-sourced microservices. Each skill knows which stage is appropriate and what signal justifies advancing.

### Design Patterns (`patterns:*`)

Provides structured guidance for applying common software patterns at the right time.
The plugin exposes a single skill, `patterns:using-patterns`, whose body is the routing
surface. Each pattern's full guidance lives in a reference under
`patterns/skills/using-patterns/references/patterns/<name>.md`, loaded on demand.

`patterns:using-patterns` is the bootstrap and router: it names the pattern that fits a
design pressure and points at its `references/patterns/<name>.md`.

The patterns it routes to (each a `references/patterns/<name>.md` reference): aggregate,
arrange-act-assert, bootstrap-and-service, builder, configuring-feature-flags,
configuring-logging, domain-objects, emitting-logs, errors-typed-untyped, newtype,
parse-dont-validate, repository, triangulate, type-conversion, type-states,
unit-of-work, using-feature-flags, visibility.

### Research (`research:*`)

Selects the right research strategy based on what kind of question is being asked.

| Skill | When to use |
|-------|-------------|
| `research:using-research` | Bootstrap — establishes when to invoke each research skill |
| `research:archaeology` | Why did this code change? Who introduced it? When was it added or removed? |
| `research:codebase` | What does this code do right now? Where is a symbol defined or used? |
| `research:dependencies` | What version of a dependency is used? What does a package provide or require? |
| `research:domain` | What does this concept mean in the domain? How are domain terms defined? |
| `research:internal` | What do internal documents (Slack, Confluence, Linear, Notion) say about this? |
| `research:public` | What does the public internet say? What do official docs or forums say? |


## License

MIT
