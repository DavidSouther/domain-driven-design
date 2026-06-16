# Better Patterns

Plan is often skipping looking for patterns. It should have a dedicated "look for applicable patterns" phase before writing out the larger plan.

Also the patterns as individual skills use too much context window for description. Let's rewrite them so that there's one "using-patterns" skill which activates during design, plan, and review phases. When designing, it should encourage using the patterns, but not be prescriptive on their specific shape. When planning, it should be presecriptive on the shape and form, so the plan includes enough that the implementation chooses the pattern shape. Review does a bit of both - when reviewing a design, it needs to suggest patterns that weren't used but would apply, and discourage patterns that were used but shouldn't apply. It should do similar during a code review.
