---
name: git-workflow
description: Use when performing source code tasks that change the working tree.
---

This Git workflow describes a rebase-oriented feature-branch git flow with final merge commits.

## Feature Branch

Development should happen in a feature branch with the same name as the topic, `YYYY-MM-DD-A-<topic>`.

## Ensure the working directory is clean

If `git status` shows any files, ask the user whether they want to continue with a dirty working directory or pause and clean it up.

Use `git switch` to change branches.

## Pull main and rebase

Prefer rebase over merge. Feature branches are per-developer, so force-pushing after a rebase is safe and expected. Keep history linear: reviewers read a PR commit-by-commit, and a linear sequence is easier to follow than a branch-and-merge graph even when the PR will land via squash-merge.

When main has moved forward:

1. `git fetch origin main`
2. `git rebase origin/main` from the feature branch
3. Resolve conflicts per replayed commit, then `git rebase --continue`
4. `git push --force-with-lease` to update the remote feature branch

Use `--force-with-lease`, never plain `--force`, so a concurrent push from another machine is not silently overwritten.

Rebase before opening a PR and again before requesting re-review if main has advanced. Do not rebase a branch that another developer is actively committing to; coordinate or merge instead.

## Commit hygiene

Shape commits such that each is a coherent step. Use `git rebase -i origin/main` to squash fixups, reorder, or reword. A clean series of small commits makes review faster even though the final merge collapses them. Before running `git rebase -i`, first write a plan with specific tasks to accomplish at each step of the rebase. As the rebase progresses, watch for merge conflicts. If there are merge conflicts, generally attempt to use `git checkout --theirs` to take the development branch. Otherwise, use `thinking` to develop a plan to resolve the merge conflicts. `git rerere` will record the resolutions for future rebases.

