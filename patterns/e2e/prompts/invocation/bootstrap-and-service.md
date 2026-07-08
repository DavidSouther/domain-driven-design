Our `POST /orders` route handler parses the request body, runs the order business rules, and talks to the database all inline, so we can't test the use case without standing up HTTP and a real database.
Restructure it: the HTTP handler should be a thin adapter that only translates protocol details, the use case should live in a service that knows nothing about HTTP (no request/response/status types in its signature), and all concrete wiring (the database repository) should happen in one place at startup.
Show the handler, the service, and the startup wiring.
