Design the failure type for a library function `fetchUser(id)` that can fail in three distinct ways the caller must handle differently: a network error (the caller should retry), a not-found (surface to the user), and a parse error (give up).
The caller must be able to tell these apart and react to each programmatically.
Then show how an application's HTTP handler consumes that failure and turns it into a log line and a response a human reads.
Show the failure type, `fetchUser`'s signature, and the handler's translation step.
