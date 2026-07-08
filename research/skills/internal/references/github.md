# GitHub

The code-collaboration surface.
First stop for issues, pull requests, and the technical discussion that happens around a change rather than in the diff.

## What it provides

- **GitHub issue/PR search**: issue and PR hits with number and URL, filterable by repo and label.
- **GitHub issue/PR fetch**: the body, comments, and diff threads where exposed, given a repo + number.

## MCP/connector

Two transports, probed in order:

- **GitHub MCP**: probe the configured GitHub MCP for this org first; tool names vary by which server you install, so discover the surface rather than assuming a slug.
- **`gh` command-line tool fallback**: if you haven't configured an MCP, fall back to the `gh` command-line tool: `gh issue list`/`gh issue view`, `gh pr list`/`gh pr view`, `gh search issues`.
  Authenticated by `GH_TOKEN` / `GITHUB_TOKEN` or an existing `gh auth login` session.

If you haven't set a token and no MCP authenticates, GitHub capabilities will not function.

## Auth

A PAT in `GH_TOKEN` / `GITHUB_TOKEN`, or a `gh auth` session; see [`auth.md`](auth.md).
This is the one default source that authenticates from an env-var token rather than a browser OAuth flow.

## Contract mapping

- *GitHub issue/PR search* → the MCP's search tool, or `gh search issues` / `gh pr list` with the query and optional repo/label filter.
  Returns issue and PR hits with number and URL.
- *GitHub issue/PR fetch* → the MCP's read tool, or `gh issue view <n>` / `gh pr view <n>` in the target repo.
  Returns body, comments, and diff threads where exposed.

## Smoke-test

Search issues in a known repo, confirm hits carry number and URL, then fetch one issue by repo + number.
A 401 / `gh: authentication` error means the token rotated or expired (a re-verification trigger, see [`auth.md`](auth.md)).
