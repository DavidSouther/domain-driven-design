# Fail Without Project Tooling

Ailly and agents are good at picking up tooling and project norms, especially those documented in README files and encoded in package files. Agents are also very good at just using other tools when they start having issues.

Ailly should be substantially more adamant at stopping and asking for guidance when it can't use a tool that's declared for the project. It should start by checking whether /initialize skills might help determine loading the tool locally (eg a missing mise trust or npm install). Then it should escalate troubleshooting _back to the user_, with what failed, suggested remediations, and why that is correct. After the user remediates, or gives Ailly permission to remediate, Ailly can retry what it was doing and continue with the task.

This should be a reference or resource that gets loaded after Ailly encounters a tool failure.
