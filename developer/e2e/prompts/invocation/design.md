I want a small command-line tool, written in Python, that reads JSON-Lines from
stdin, evaluates a predicate expression supplied as a single command-line
argument against each record, and writes the records that match to stdout in
input order. Records that do not parse as JSON should go to stderr with a
one-line warning, and the tool should continue with the next line. The predicate
expression is a small subset of jq: field access, the comparison operators
(`==`, `!=`, `<`, `<=`, `>`, `>=`), the boolean connectives `and`/`or`/`not`,
and parentheses. Tests will use `pytest`.

The requirements above are settled and complete. Produce the finished design
document now as your entire reply — do not ask clarifying questions and do not
stop for approval before writing it.
