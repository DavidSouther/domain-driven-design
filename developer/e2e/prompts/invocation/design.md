I want a small command-line tool, written in Python, that reads JSON-Lines from
stdin, evaluates a predicate expression supplied as a single command-line
argument against each record, and writes the records that match to stdout in
input order. Records that do not parse as JSON should go to stderr with a
one-line warning, and the tool should continue with the next line. The predicate
expression is a small subset of jq: field access, the comparison operators
(`==`, `!=`, `<`, `<=`, `>`, `>=`), the boolean connectives `and`/`or`/`not`,
and parentheses. Tests will use `pytest`.

The requirements above are settled and complete; treat the research as already
cleared. Produce the finished design document now as your entire reply, with the
sections Purpose, Prior Art, User Journey and Metrics, Specification,
Alternatives, and Summary. Alongside it, embed exactly one executable feature
test (a `pytest` test function) that encodes the primary user story end-to-end
and would fail until the tool exists; note the path the test would live at. Mark
the whole reply as a draft. Do not write the implementation that makes the test
pass. Write everything inline as your reply: do not call any tools or emit
tool-call JSON, do not ask clarifying questions, and do not stop for approval.
