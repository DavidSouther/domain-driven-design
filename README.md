# DDD & Design Patterns Skills for Claude Code

A [Claude Code](https://claude.ai/code) plugin providing structured workflows for Domain-Driven Design and software design patterns.

## Skills

### Domain-Driven Design (`ddd:*`)

Guides architectural decisions and domain modeling through the full DDD lifecycle.

| Skill | When to use |
|-------|-------------|
| `ddd:using-ddd` | Bootstrap — establishes when to invoke each DDD skill |
| `ddd:domain-model` | Starting a new project, service, or feature with business logic |
| `ddd:ubiquitous-language` | Naming entities, operations, or domain concepts |
| `ddd:glossary` | Any ambiguous or potentially synonymous term appears |
| `ddd:contracts-and-invariants` | Designing API boundaries, service interfaces, or domain operations |
| `ddd:arrow-of-maturity` | Evaluating architecture, adding persistence, or feeling scaling pressure |

The Arrow of Maturity describes six architectural stages a DDD project grows through, from prototype scripts to event-sourced microservices. Each skill knows which stage is appropriate and what signal justifies advancing.

### Design Patterns (`patterns:*`)

Provides structured guidance for applying common software patterns at the right time.

| Skill | When to use |
|-------|-------------|
| `patterns:using-patterns` | Bootstrap — establishes when to invoke each pattern skill |
| `patterns:newtype` | A primitive type represents a distinct domain concept |
| `patterns:entities-value-objects-services` | Deciding what has identity, what is a value, what is a function |
| `patterns:builder` | Object construction with many fields or required/optional distinction |
| `patterns:parse-dont-validate` | Data arrives from an external boundary (HTTP, input, file, queue) |
| `patterns:type-states` | Modeling a state machine or finite set of mutually-exclusive states |
| `patterns:repository` | Decoupling domain logic from a specific storage technology |
| `patterns:aggregate` | Operations that must transition domain state atomically |
| `patterns:unit-of-work` | Bridging an Aggregate with a Repository in a single transaction |
| `patterns:bootstrap-and-service` | Wiring concrete dependencies and separating domain from HTTP/CLI |

## Installation

Install via the Claude Code marketplace using the plugin manifest:

```json
{
  "source": "https://github.com/davidsouther/ddd_skill"
}
```

Or reference the local `ddd` or `domain` directories directly in your marketplace config.

## License

MIT
