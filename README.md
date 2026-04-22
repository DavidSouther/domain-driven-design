# DDD & Design Patterns Skills for Claude Code

A [Claude Code](https://claude.ai/code) plugin providing structured workflows for Domain-Driven Design, software design patterns, research, and a strict test-driven developer lifecycle.

## Skills

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

### Developer (`developer:*`)

A strict three-loop development lifecycle: design → feature test → TDD implementation.

| Skill | When to use |
|-------|-------------|
| `developer:using-developer` | Bootstrap — establishes which developer skill to invoke for the current situation |
| `developer:brainstorming` | Exploring a new idea or clarifying requirements before writing a design doc |
| `developer:design-doc` | Formatting or structuring a design doc |
| `developer:feature-test` | Writing the feature test after design is approved |
| `developer:initialize` | Setting up a new project or language environment |
| `developer:planning` | Breaking a failing feature test into implementation steps |
| `developer:red-green-refactor` | Implementing a plan step with TDD |
| `developer:refactor` | Tests are green; cleaning up code before continuing |
| `developer:run` | Starting or resuming a feature development session |
| `developer:thinking` | Stuck on a compiler error or test failure during TDD |
| `developer:writing-plans` | Converting a spec or requirements into a general implementation plan |

The developer lifecycle uses draft gates: each artifact (design doc, feature test, plan) must be human-reviewed and cleared before the next loop begins.

### General (`general:*`)

Utilities for skill authoring, parallel agent dispatch, and git worktree isolation.

| Skill | When to use |
|-------|-------------|
| `general:using-general` | Bootstrap — load before any action to find the most relevant skills |
| `general:using-git-worktrees` | Starting feature work that needs isolation from the current workspace |
| `general:dispatching-parallel-agents` | Multiple independent tasks with no shared state or sequential dependencies |
| `general:writing-skills` | Creating, editing, or verifying skills before deployment |

## Installation

Install via the Claude Code marketplace using the plugin manifest:

```json
{
  "source": "https://github.com/davidsouther/domain_driven_design"
}
```

Or clone and install locally with `claude /plugin install ./`.

## License

MIT
