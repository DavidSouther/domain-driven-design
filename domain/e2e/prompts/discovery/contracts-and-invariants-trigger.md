The payments context already exists and its bounded context is well understood. I am about to write the public API for it — the operation signatures other services will call. The ledger must never be observable in an unbalanced state, but the current signatures say nothing about that guarantee or about which inputs are required.

Which domain ability applies, and where is its guidance?
