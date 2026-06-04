All tests are green on the auth-handler change — static checks pass, the unit
tests pass. Looking at the diff, I see three places where I duplicated the
bearer-token parsing logic and one method that grew past 60 lines. I want to
clean this up before opening the PR. No behavior needs to change.

Name the single `developer:*` skill I should invoke right now, and one sentence
on why.
