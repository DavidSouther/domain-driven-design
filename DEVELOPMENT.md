# Development

## Release Script Tests

```sh
PYTHONPATH=.github/scripts python3 -m unittest discover -s .github/scripts/tests
```

## Verified commits and main branch protection

Commits are verified using git configuration, and main branch has strict protections. All changes must go through PR from a branch. Branches and commits use conventional commit messages.

## Project Management

Issues tracked in Github under DavidSouther/domain-driven-design.

## Evals

Feature and unit tests for Ailly should be in the form of evals. Feature tests are authored in the root e2e/ folder; unit tests are authored in individual plugin e2e/ folders.
