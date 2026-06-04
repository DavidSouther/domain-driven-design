I'm in a red-green-refactor cycle on Step 1 of the jq-lite plan (the predicate
parser, Python). I wrote the parser, wrote one test, and ran `pytest`. The test
does not fail the way I expect — it errors out before asserting. I changed the
recursion to start from a different rule and got the exact same error again.

Exact error:

```
RecursionError: maximum recursion depth exceeded
  File "jqlite/parser.py", line 14, in parse_expr
    left = self.parse_expr()
  File "jqlite/parser.py", line 14, in parse_expr
    left = self.parse_expr()
  [Previous line repeated 996 more times]
```

The code I changed in this step:

```python
class Parser:
    def parse_expr(self):
        left = self.parse_expr()          # <- changed this line
        op = self._eat_comparison_op()
        right = self.parse_term()
        return Compare(left, op, right)
```

Plan step: "Step 1: Predicate parser — recursive-descent parser that turns the
predicate string into an AST of comparison and boolean nodes."

I'm stuck. Produce the analysis that tells me what is actually wrong and the
concrete ordered steps to fix it. Do not edit any files and do not propose
"try something and see what happens".
