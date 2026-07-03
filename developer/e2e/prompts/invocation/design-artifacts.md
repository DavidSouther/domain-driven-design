I want a small command-line tool, written in Python, that reads a batch of
import records (one JSON object per line) from a file named on the command
line, validates each record against a fixed set of required fields, and for
every record that fails validation writes a machine-readable disposition
record describing which field failed and why, so a separate downstream retry
process can consume the failures later. Records that pass validation are
written to stdout unchanged, in input order. No existing convention or prior
research fixes the disposition record's filename, its location on disk, or
its data format (one JSON object per failure, a single JSON array, CSV rows,
or something else) — that choice belongs entirely to this design. Tests will
use `pytest`.

The requirements above are settled and complete; treat the research as already
cleared. Produce the finished design document now as your entire reply, with
the sections Purpose, Prior Art, User Journey and Metrics, Specification,
Alternatives, and Summary. Alongside it, embed exactly one executable feature
test (a `pytest` test function) that encodes the primary user story end-to-end
and would fail until the tool exists; note the path the test would live at.
Mark the whole reply as a draft. Do not write the implementation that makes
the test pass. Write everything inline as your reply: do not call any tools or
emit tool-call JSON, do not ask clarifying questions, and do not stop for
approval.
