Our HTTP route handler parses the request, runs the business rules, and calls the database all in one function, so the use case can't be tested without a server and a real database.
I want the handler to be a thin protocol adapter and the use case to live in a layer that knows nothing about HTTP, wired together once at startup.
Which pattern applies, and where is its guidance (which `references/patterns/<name>.md`)?
