All tests are green on the auth-handler change — static checks pass, the unit
tests pass. Looking at the diff, I see three places where I duplicated the
bearer-token parsing logic and one method that grew past 60 lines. I want to
clean this up before opening the PR. No behavior needs to change.

Name the single developer ability or coordinator phase that applies right now,
name the `references/...` reference the `developer:ailly` coordinator loads for it
(a `references/<ability>.md` for a progressive ability, a
`references/phases/<phase>.md` for a lifecycle phase), and one sentence on why.
