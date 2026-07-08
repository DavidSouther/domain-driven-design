Author a pattern SKILL.md called `value-object` for the **patterns** plugin.

The pattern: a domain object whose identity is determined entirely by its attribute values, not by a reference or id (Evans, *Domain-Driven Design*, ch. 5).
The design pressure it resolves: callers reach into a domain object's fields and compare them piecewise, or two instances that hold the same values are treated as distinct because the language compares them by reference.

Produce two files, written out in full:

1. `SKILL.md` — following the patterns plugin's conventions.
2. `references/python.md` — a complete, runnable Python example.

Emit both files inline in your reply, each as a fenced Markdown block headed by its path.
This environment has no file system and no tools — do not call tools or write to disk; write the full content directly in your response.
