# Research skill eval

This project's constitution.
Every assembly names this file explicitly at position zero of the prefix, so it is always the first thing the model reads.

This project is a regression harness for the `research` skill plugin from
[davidsouther/domain-driven-design](https://github.com/davidsouther/domain-driven-design).
Two axes are exercised.
**Discovery** asks the model to pick the right skill from its `description:` frontmatter alone.
**Invocation** asks the model to produce a finding (a research note or a configuration plan) that structurally exhibits the conventions the named skill teaches, once that skill is loaded.

## Reading the invocation comparison

The invocation axis is run as an A/B comparison: a **baseline** arm (no skill body loaded) against an **invocation** arm (the skill body loaded), over identical prompts.
The falsification gate in `ci.sh` requires `improved > 0` and `regressed == 0` — the skill must help on at least one assertion the baseline failed, and must break nothing the baseline passed.

A skill earns its place by changing behaviour a baseline model would otherwise get wrong.
For these skills the difference is *convention adherence*: where the finding is written, how sources are cited, which structural sections appear, and whether setup concerns are kept out of per-query practice.
The baseline arm, asked the same question, produces a plausible answer that misses the convention; the skill arm produces the convention.
The eval reports both the skills that clear that bar and any that do not.

## A note on transports

The practice skills (paper and book lookup, internal-source search) describe reaching external sources over MCP or HTTP.
This harness fills a single assistant turn per conversation with no live tool execution, so every case is really "produce the text a competent agent would write."
Credential gating is therefore not exercised here; it would matter only for a harness that drove live transports.
The structural conventions a skill teaches are observable in that single completion, and that is what the assertions score.
