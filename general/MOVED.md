Ailly moved to https://github.com/davidsouther/ailly. This install comes from davidsouther/domain-driven-design, which gets no further updates.

Tell the user once and offer to repoint the install. Run nothing until they agree, and drop the topic if they decline. Skip any harness whose `ailly` marketplace already points at davidsouther/ailly or at a local checkout.

- Claude Code: note each `@ailly` plugin and its scope from `claude plugin list`, then run `claude plugin marketplace remove ailly`, `claude plugin marketplace add davidsouther/ailly`, and `claude plugin install <plugin>@ailly --scope <scope>` for each.
- Codex: `codex plugin remove <plugin>@ailly` for each installed plugin, `codex plugin marketplace remove ailly`, `codex plugin marketplace add davidsouther/ailly`, then `codex plugin add <plugin>@ailly` for each.
- pi: find the legacy source in `pi list`, then `pi remove <source>` and `pi install git:github.com/davidsouther/ailly`.

Restart the harness afterward.
