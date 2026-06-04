My application handler loads an order, mutates it, and saves it, but a failure
partway through can leave a partial write. I want the load, the domain operation,
and the persistence wrapped in one durable transaction that commits together or
rolls back entirely, testable without a real database. Which `patterns:*` skill
applies?
