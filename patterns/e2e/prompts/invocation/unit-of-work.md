An application handler must load an `Order` aggregate, run one domain operation on it, and persist all the resulting changes atomically: if anything fails partway, nothing is written.
Implement the handler so the load → mutate → save happens inside a single transactional boundary that commits on success and is guaranteed to roll back on any error, with the session/transaction never leaking into the domain.
Also provide a test double that needs no database.
Show the transactional abstraction, the handler, and the test double.
