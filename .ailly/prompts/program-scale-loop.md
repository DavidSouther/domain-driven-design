# Research: Program-Scale Loop for Ailly

## Background

Ailly currently has three delivery scales:

- **Bug loop** - one failure in an existing feature, possibly part of a larger suite of issues, but generally amenable to a TDD quickloop. Duration: hours.
- **Feature loop** — one component or capability, exits when a single executable feature test is green. Duration: hours to days.
- **Project loop** — several features that only deliver value together, exits when a Closing Bell usability study passes. Duration: days to weeks.

A comparison with the Compound Engineering plugin (`EveryInc/compound-engineering-plugin`) surfaced a gap above both of these.

CE's `ce-strategy` skill operates at product-identity level: it captures the target problem, guiding approach, primary persona (JTBD framing), key metrics, and investment tracks. It is positioned as "upstream of the loop" — a durable anchor at the repo root that grounds every brainstorm and plan session without being consumed by any of them. Ailly has no equivalent. The closest things are the project design doc's Purpose section (scoped to one delivery) and the README (which describes the plugin itself, not projects built with it). Neither captures metrics, explicit scope exclusions, or a structured JTBD persona.

The key realization from this comparison: the missing concept is not "strategy" but **program**.

A **project** has a specific ending — a Closing Bell, a ship date, a deliverable. A **program** is a series of overlapping projects that together deliver a strategic vision. It has no single exit criterion; it continues as long as the vision is being pursued. Individual projects complete and are archived; the program persists and absorbs the next project.

This maps onto the scale hierarchy:

```
Program — ongoing strategic vision; no ending; absorbs projects as they complete
  └─ Project — bounded deliverable; exits at Closing Bell; composed of features
    └─ Feature — executable test; exits at green; composed of TDD increments
      └─ Bug/Fix — small, reproducible defect or unexpected behavior; "minimal" quick fix
```

## What the Research Should Address

### 1. Is "program" the right term?

Program management has an established meaning in enterprise software (PMI, SAFe, etc.). Examine whether that framing matches the intent here, or whether a different term (portfolio, initiative, track, product) better captures the concept: a series of overlapping, sequenced projects unified by a strategic purpose, with no predetermined end.

### 2. What artifacts does a program produce?

A project produces a design doc, a plan, per-feature designs, a Closing Bell, and eventually a completed record. A program presumably produces something analogous — a document that captures the strategic vision, the current and planned projects, and the measures of progress — but the program document is never "completed," only updated.

Candidates to examine:
- CE's `STRATEGY.md` structure (target problem, approach, persona, metrics, tracks) as a starting point
- Rumelt's strategy kernel (diagnosis, guiding policy, coherent action) as a theoretical grounding
- How existing program-management frameworks handle the distinction between a program's vision and a project's scope

### 3. How do projects within a program relate?

Ailly's project loop already handles sequential and parallel feature-steps within one project. The equivalent at the program level is how projects within the program relate — dependencies between projects, shared interfaces settled before parallel projects begin, and how a completed project's outputs feed into the next.

Research whether there are useful models for this that do not simply replicate the project loop's sequential/parallel tagging at a higher level of abstraction.

### 4. What is the "Closing Bell" equivalent for a program, if any?

A project has a usability study as its exit criterion. A program, if it has no predetermined end, probably does not have a single exit criterion. But it likely has milestone signals — moments when a project's completion advances the program's strategic position in a measurable way. Research how ongoing programs track strategic progress without a single shipped artifact as the measure of done.

### 5. Where does the STRATEGY.md interview discipline fit?

CE's `ce-strategy` is valuable not just for what it stores but for how it collects the information — structured pushback on weak answers, Rumelt-style anti-patterns, one-section-at-a-time interview. That discipline could live in a program-initialization skill, or it could be a separate concern. Research whether the interview mechanics should be part of program setup or abstracted into a general `domain:strategy-interview` pattern.

### 6. Existing prior art in Ailly's skill ecosystem

Ailly already has `domain:arrow-of-maturity` (architectural stage progression), `domain:domain-model` (subdomain and bounded context identification), and `domain:contracts-and-invariants`. Research whether any of these already address program-scale concerns or could be extended to do so, before proposing a net-new skill.

## Hypothesis to Test

A **program** skill for Ailly would:

- Live above the project loop in scale, as the project loop lives above the feature loop
- Produce a long-lived anchor document (call it `program.md` or `PROGRAM.md`) that captures the strategic vision, current and planned projects, and progress measures
- Include an interview discipline (drawing from CE's `ce-strategy` and Rumelt) to prevent the document from becoming a goal dressed as a vision
- Guide project sequencing within the program, analogous to how the project loop guides feature sequencing within a project
- Not replace `project-cycle.md` but extend it: a project always belongs to a program, and the program document is the place where a newly completed project's Closing Bell results update the overall strategic picture

Whether this hypothesis survives depends on whether the research finds prior art that falsifies it, a simpler model that subsumes it, or evidence that the project loop already covers the use cases at this scale.

## Scope

This is a research phase for a new Ailly skill or skill group. The deliverable is a `research.md` summarizing:

- What "program" means in this context (terminology settled)
- What artifacts a program produces and what their lifecycle looks like
- How the program loop relates to the project loop structurally
- What existing prior art (CE, PMI, SAFe, Rumelt, domain-driven design at scale) applies
- A recommendation: is a new `developer:program` skill warranted, and if so, what is its minimal viable form?

The research should be opinionated enough to set up a design phase, not a neutral survey.
