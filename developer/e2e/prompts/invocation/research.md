I have a vague itch but nothing gathered yet.
Our team keeps hand-rolling retry logic around flaky network calls, and every service does it a little differently.
I think we want some kind of shared retry helper, but I have not written a problem statement, looked at prior art, or decided on scope.
Nothing exists yet.

Open the research phase for this topic.
Gather supporting context (an expand pass over how this class of problem is usually solved and what already exists), then a refine pass that sizes it (is this a project of several features, a single feature, or really just a bug in one service, could an off-the-shelf library do it, what is the smallest version that meets the need).
Produce the `research.md` document now as your entire reply: write it inline, do not call any tools or emit tool-call JSON, do not ask clarifying questions first, and mark it as a draft for me to review.
