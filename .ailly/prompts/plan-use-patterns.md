# Plan beat: look for applicable patterns

Before writing out the larger plan, run a dedicated "look for applicable patterns"
beat. Consult `patterns:using-patterns` (its body is the routing surface), match the
design pressures in the feature against the routing table, and name the patterns that
apply. For each named pattern, point at its reference under
`references/patterns/<name>.md` so the plan carries the guidance, not just the name.

The prescriptiveness of this beat varies by phase:

- **During design:** encourage applicable patterns without fixing their shape. Name the
  pattern and the pressure it relieves; leave the concrete form open so design stays
  about alternatives, not implementation.
- **During plan:** prescribe the shape and form. Name each applicable pattern and write
  enough into the plan (the type or interface shape it implies, the discriminator that
  selects it over a near neighbour) that the implementation step can adopt the pattern
  without re-deciding which one to use. The implementation still chooses the exact code,
  but the plan fixes which pattern and roughly what it looks like.
- **During review:** do both. When reviewing a design or a plan, suggest patterns that
  were not used but would apply, and discourage patterns that were used but should not.
  Apply the same lens to a code review.

Name the applicable patterns explicitly. A plan that silently skips this beat is
incomplete; surface "no pattern applies here" as a deliberate finding rather than an
omission.
