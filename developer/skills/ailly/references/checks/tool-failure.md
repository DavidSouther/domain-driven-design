# Tool failure: stop and escalate

Load this reference **after** a tool declared for the project fails: a build, test,
lint, type-check, package manager, or task runner that the README or a package/lock
file says this project uses.

Agents are good at picking up project norms, and good at quietly routing around a
broken tool by reaching for a different one. That second instinct is the hazard here.
When a *declared* tool fails, silently substituting another tool hides a real problem
and produces results the project's own tooling would not endorse.

## Be adamant

When a declared tool fails, **stop**. Do not silently substitute another tool, and do
not work around the failure by hand. A declared tool failing is a signal worth
surfacing, not an obstacle to route past. The bar for stopping here is deliberately
higher than for an undeclared, incidental tool.

## First: check for a local fix via the initialize reference

Many failures are a missing local setup step, not a broken project. Before escalating,
consult the coordinator's initialize reference
(`developer/skills/ailly/references/abilities/initialize.md`) to see whether you need to prepare the environment, for example a missing `mise trust`, an `npm install` that has not
been run, an unactivated virtualenv, or an uninstalled dev dependency. If the initialize
reference identifies a safe, local, idempotent fix, apply it and retry the original
command once.

## Then: escalate back to the user

If `initialize` does not resolve it, escalate to the **user**. Do not keep trying
variations silently. Report, in plain terms:

- **What failed** — the exact command and the relevant error output.
- **Suggested remediation** — the most likely fix (for example, `mise install`, a version
  bump, an auth/token that needs setting, a missing system dependency).
- **Why that remediation is correct** — the reasoning that connects the error to the fix,
  so the user can judge it rather than apply it blindly.

## Finally: retry and continue

After the user remediates, or explicitly gives permission to apply the suggested
remediation, retry the command that failed and continue the task from where it stopped.
