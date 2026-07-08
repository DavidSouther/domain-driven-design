A `Connection` moves through two phases: it is either open or closed.
You may only `send` on an open connection and only `reopen` a closed one.
Today it is a single class with a boolean `isOpen` field and runtime guards, so `send` on a closed connection only fails at runtime.
Model the phases so that calling `send` on a closed connection is a compile error rather than a runtime check, and so a transition cannot leave a stale handle to the pre-transition state usable.
Show the types and one transition.
