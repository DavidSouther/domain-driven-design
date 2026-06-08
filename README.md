# DDD & Design Patterns Skills for Claude Code

A [Claude Code](https://claude.ai/code) plugin providing structured workflows for Domain-Driven Design, software design patterns, research, and a strict test-driven developer lifecycle.

## Installation & Getting Started

1. Clone the repository locally.
2. Add the marketplace: in Claude Code, run `/plugin marketplace add <path-to-clone>`, where `<path-to-clone>` is the cloned repository directory.
   * You can also run `/plugin` to open the interactive browser and add it from the **Marketplaces** tab.
3. Install the skills with `/plugin install <name>@ailly` — install `general`, `developer`, `patterns`, and `research` (`domain` is optional). Browse and toggle them anytime from the **Installed** tab of `/plugin`.
4. Start a project in a new folder - `/ailly /initialize a project called [name] for [design goal] using [TypeScript, Python, or Rust] (including initializing git)`.
5. Start work on new feature in that folder - `/ailly start a new feature for [user need]`.
6. Continue work on whatever you did last - `/ailly continue`
7. Tell Ailly to do research herself - after Ailly asks you a question, `/using-research to perform a deep dive; pay attention especially to [area of interest]`.
8. Tell Ailly to fix a bug - `/ailly quick loop fix [the bug]`.

To update Ailly, simply pull the latest sources in the git repo, and reload the coding agent.

### Useful Patterns

- Develop a complex prompt in `./docs/prompts/big-prompt.md`, then run it with `run ./docs/prompts/big-prompt.md`.
- Check if Ailly has what she needs for research - `/ailly check if internal, books, and papers research are set up right`
- Figure out really anything about Ailly - ask her! `/ailly what skills are available?` `/ailly how do I update a git repo?`
- Change the `docs/` folder by adding `For developer: tools, .agents/ instead of .docs` to CLAUDE.md (or AGENTS.md if CLAUDE.md includes it).

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

| Skill | When to use |
|-------|-------------|
| `patterns:using-patterns` | Bootstrap — establishes when to invoke each pattern skill |
| `patterns:aggregate` | Operations that must transition domain state atomically |
| `patterns:arrange-act-assert` | Writing any test to ensure clear setup, single action, and focused assertions |
| `patterns:bootstrap-and-service` | Wiring concrete dependencies and separating domain from HTTP/CLI |
| `patterns:builder` | Object construction with many fields or required/optional distinction |
| `patterns:entities-value-objects-services` | Deciding what has identity, what is a value, what is a function |
| `patterns:newtype` | A primitive type represents a distinct domain concept |
| `patterns:parse-dont-validate` | Data arrives from an external boundary (HTTP, input, file, queue) |
| `patterns:repository` | Decoupling domain logic from a specific storage technology |
| `patterns:triangulate` | A hardcoded implementation passes the first test and the right generalization is not yet obvious |
| `patterns:type-states` | Modeling a state machine or finite set of mutually-exclusive states |
| `patterns:unit-of-work` | Bridging an Aggregate with a Repository in a single transaction |

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
