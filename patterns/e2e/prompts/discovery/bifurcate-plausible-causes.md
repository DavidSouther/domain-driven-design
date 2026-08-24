After initial debugging, three plausible root causes remain: stale cache data,
a database write that never commits, or broken retry logic. Obvious guesses and
recent-change theories haven't panned out. I need the next move to be a test or
probe that eliminates (or isolates) substantial portions of the system, not
another unstructured trace. Which pattern applies, and where is its guidance
(which `references/patterns/<name>.md`)?
