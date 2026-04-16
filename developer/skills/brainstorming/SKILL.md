---
name: brainstorming
description: "Use when design exploration needs visual treatment — UI mockups, wireframes, layout comparisons, architecture diagrams, or side-by-side visual options. Launches an interactive browser-based visual companion."
---

# Visual Design Companion

Browser-based tool for exploring visual design questions interactively. Shows mockups, wireframes, layout comparisons, and architecture diagrams in a live browser window with click-to-select interactions.

## When to Use

**Use the browser** when the content itself is visual:
- UI mockups and wireframes
- Side-by-side layout comparisons
- Architecture diagrams rendered spatially
- Design polish questions (spacing, hierarchy, visual style)
- Spatial relationships (state machines, entity-relationship diagrams)

**Stay in the terminal** when the content is text:
- Requirements and scope questions
- Conceptual A/B choices described in words
- Tradeoff lists and pros/cons tables
- Technical decisions (API design, data modeling)

A question *about* a UI topic is not automatically visual. "What kind of wizard?" → terminal. "Which wizard layout?" → browser.

## Offering the Companion

When visual questions are coming, offer it in its own message — nothing else in that message:

> "Some of what we're working on might be easier to explain if I can show it to you in a web browser. I can put together mockups, diagrams, comparisons, and other visuals as we go. This feature is still new and can be token-intensive. Want to try it? (Requires opening a local URL)"

Wait for the user's response before continuing. If they decline, proceed with text-only description.

## Starting a Session

```bash
scripts/start-server.sh --project-dir /path/to/project
# Returns: {"url":"http://localhost:52341","screen_dir":"...","state_dir":"..."}
```

Save `screen_dir` and `state_dir`. Tell the user to open the URL.

## The Loop

1. **Write HTML** to a new file in `screen_dir` (use Write tool — never cat/heredoc)
2. **Tell the user** the URL and a brief description of what's on screen; end your turn
3. **Next turn:** read `$STATE_DIR/events` for browser clicks, merge with terminal text
4. **Iterate or advance** — push `waiting.html` when returning to terminal questions

## Full Reference

When the user accepts the companion, read the full guide before proceeding:
`skills/brainstorming/visual-companion.md`
