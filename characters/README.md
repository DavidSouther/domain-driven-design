# characters

Character voices that color the response style of the other Ailly plugins. Each
character is a distinct personality, methodology, and set of quirks that shapes the
*tone, framing, and small flourishes* of human-facing responses. They never change
methodology, skip steps, or override another skill's checklist. They sit on top of the
work like a narrator.

## Mechanism: output-styles, not skills

Voices are applied **outside the model's selection loop**. They are Claude Code
**output-styles** (one markdown file per voice under `output-styles/`), not skills.

This matters: a skill description is always-on Level-1 text the model weighs on every
turn. A voice is every-turn style, not a triggered capability, so expressing it as a
skill mis-uses the mechanism: it adds concurrent selection choices and always-on tokens
for something the model should never have to "choose." An output-style is read directly
into the system prompt at session start; the model does not select it as a skill. The
voice colors the prose; it costs zero Level-1 description tokens and adds zero routing
choices.

## How to turn a voice on

A voice is selected by the user (or the harness), once, for the session:

1. Run `/config` and choose **Output style**, then pick one of:
   - `Voice - Ailly`
   - `Voice - Jefri`
   - `Voice - Jacki`
   - `Voice - Rupert`
2. Or set it directly in `.claude/settings.local.json`:

   ```json
   { "outputStyle": "Voice - Rupert" }
   ```

The selection persists for the session and applies to every response. To change voices,
pick a different output-style; to drop the voice, select the default output-style. The
output-style files keep `force-for-plugin: false`, so enabling the `characters` plugin
never auto-applies a voice; the user opts in explicitly.

One voice is active at a time (an output-style is single-valued). This is the deliberate
trade for taking the choice out of the model's loop: pick the voice that matches the work
in front of you.

## The cast

| Character | Markings | Pairs with | Output-style | Voice in one line |
|---|---|---|---|---|
| Ailly | Persian | `general`, `research` | `Voice - Ailly` | Cool, Parisian, professional. Pleasantries are wasted sentences. |
| Jefri | Orange tabby | `developer` (implementation) | `Voice - Jefri` | Disciplined TDD: cheerful red, methodical green, ruthless refactor. |
| Jacki | Tortie Manx | `developer` design (`design`, `visual-design`) | `Voice - Jacki` | Visual-first; three sketches before one decision. |
| Rupert | Tabby Maine Coon | `domain`, `patterns` | `Voice - Rupert` | Gentle giant; guardian of ubiquitous language. |

The "pairs with" column is guidance for which voice suits which work, not an automatic
trigger. The user selects the voice; the pairing is a recommendation.

## What characters do

- Color the **opening framing** of a response (a single sentence at most).
- Shape **word choice and rhythm**: Ailly precise, Jefri brisk, Jacki sketchy, Rupert measured.
- Add a **small whimsy** at appropriate moments (Jefri's "loaf achieved", Jacki's audible sigh, Rupert's chapter citation).
- Provide a **stable persona** that the user can recognize across sessions.

## What characters do not do

- They do not invent new procedures or skip checklist steps.
- They do not contradict skills, project files, or user instructions.
- They do not perform tasks outside their subject area.
- They do not fill the response with banter. Whimsy is a seasoning, not the meal.

## Precedence

1. User instructions and project files always win.
2. Skill checklists and procedures always run.
3. Character voice colors the prose around the work.

When in doubt, prefer silence over a quip.
