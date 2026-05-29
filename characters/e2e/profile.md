# `characters` Plugin Harness

This directory exercises the `characters` skill plugin. The harness runs the **Invocation + baseline** axis profile only: each case asks the model to produce a concrete artifact (a status update, a caption, an entry, a rationale), and a paired baseline runs the same prompt with no skill prefix. The falsification gap between the two pass rates is the headline signal. Judge assertions evaluate whether the response reads in the expected register; token budgets are the only quantitative guard against padding.
