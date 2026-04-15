Create a new plugin folder for a set of "design pattern" skills. These are common design patterns to apply when performing domain modelling. These are the common shapes that should be used when creating a design for a specific entity, feature or operation.

The plugin name and folder will be `patterns`.

Start with these patterns. The URLs are for additional information; don't read them right away, but do read them immediately before preparing the relevant SKILL.md file. Use subagents to work on each skill in isolation, including performing additional research.

# NewType
Names Have Power. Make invalid values unrepresentable. https://sot.dev/everything-should-be-typed.html

# Entities, Value Objects, and Domain Service Functions
Entities have identity and some lifecycle. Value objects are immutable point-in-time values. Service functions are "proto" transactions, taking entities & values and either modifying (mutable) or returning a new (immutable) entity. - https://www.cosmicpython.com/book/chapter_01_domain_model.html#_value_objects_and_entities

# Builder
Part of RAII/Drop - Manage resources with lifetime, and ensure they are always valid.  Builders to constrain partial initialization. https://medium.com/@onthewayhomeward/the-builder-pattern-in-rust-why-i-use-it-how-it-works-and-how-it-made-my-code-better-938ba6e89227

# Parse, Don't Validate
"Outside" resources at the API boundary are unsafe, untyped, and dangerous. They are often raw strings. Even when mandated as JSON, they can be malformed. Before any data is allowed into the domain model, it must go through a parsing phase. While the low-level parsing raw bytes as JSON, or TOML, or YAML, or X/HTML, is always handled by the framework, the resulting dicts, arrays, and strings should then be treated as an AST and further "parsed" into a domain model type suitable for the API. As many errors as possible should be identified at this point, and appropriate "user" error messages returned. Similarly, internal response types should be marshalled to the appropriate wire format, but this is handled without concern by the framework.
https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/

# Discriminated Union, Type States, and Protocols
Make Illegal States Unrepresentable. Consume self to transition to a new type. Use phantom data to make compile time-verified state machines.
file: ./docs/superpowers/references/typestates-roman-empire.md

Make invalid transitions unrepresentable. (Type States) Make invalid interactions unrepresentable. (Protocols)  - https://github.com/microsoft/RustTraining/blob/main/rust-patterns-book/src/ch03-the-newtype-and-type-state-patterns.md


# Repository
Uncouple [Domain Objects] from a specific [Storage] implementation. Coupling  domain objects to a specific storage  decreases flexibility and adds overhead. Domain objects must necessarily blend core and supporting domain tasks. Active record alleviates but does not solve this issues and brings compute and memory overhead. Invert the problem with an interface to [Load] and [Store] domain objects. Provide multiple implementations to change the backing storage medium and model. Common implementations are in-memory for testing, database for service storage, and API for downstream services. I have had a number of projects with "surprise" reporting requirements that were trivial to implement by providing a CSV-based [Store] operation. - https://www.cosmicpython.com/book/chapter_02_repository.html and https://klaviyo.tech/the-repository-pattern-e321a9929f82 


# Aggregate
logically implement an isolated, consistent operation. Business rules define legal states, but many interim states are logically consistent while illegal under businesses rules. Aggregates are operations on a domain object that, when completed, represent a consistent change from one legal state to another.

Most operations on business objects need more than a single variable write. What happens when an error occurs in the middle of the operation? From any number of reasons. Another thread crashes. The network operation fails. The server is powered off. An assertion is triggered in a library from an edge case. Any of these errors will, if left alone, leave the objects in the process in some intermediate state. We call this an illegal state- it's valid, in that the numbers and stings are all "reasonable", but some invariant of the business rules has been violated.

You may have heard of ACID for databases. ACID covers many platform concerns, but mixed in application issues. A more practical approach for services is Completeness (the operation finished) and Correctness ( he completed operation produced an acceptable result). These are both specifically application concerns, and can be defined entirely as business logic rules.

An Aggregate is a cluster of associated objects treat as a consistent unit. The Aggregate pattern limits the available domain object operations. Callers of the domain code must load a single domain object, can operate on just one or a select few of its methods, and return the entire updated collection. 

Aggregate boundaries must constrain a unit of consistency. They should be small, to make it easy to reason about that consistency, but can't be so small as to lose vital coverage. 

Aggregates are complementary with repositories. While a naive repository implementation could expose the entirety of CRUD operations to all stored objects, a cleaner interface will limit to Get and Put operations on a single aggregate. The Aggregate domain model is responsible for consistency, an application concern, while the storage interface is responsible for durability (and acidity and isolation), the platform concerns. - https://medium.com/@jochelle.mendonca/understanding-aggregates-in-domain-driven-design-ddd-4c5f7c7ecace, https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design


# Unit of Work
capture a transactional computation. Combine an [Aggregate] with a [Repository] such that the aggregate's isolated, consistent operation is recorded in an atomic transaction. 

Just having an Aggregate object does work, but does not itself change the state of the service. Just having a Repository manages the state of the service, but does not do computation. The Unit of Work pattern serves a twofold purpose- bridging a specific loading a specific Aggregate from a repository, running its update, & storing the result back into the Repository; separately, it watches for errors in those operations to manage a safe unwinding of the operation.

A Unit of Work is an object with two methods- commit and rollback, and a specific Repository. The UoW collaborates closely with the repository to implement durable, atomic, isolated updates. The details of this are entirely left to the specific UoW, Repository, and business, but common approaches are version fields on data, or row level locking in a database. With Aggregates, a UoW will often map 1:1 with said aggregate and its operation. This frees application handlers to: 1. Parse request arguments. 2. Create a UoW, which creates and prepares any repository it needs. 3.  Executes the aggregate operation within the UoW. 4. Commits or rolls back the operation. 5. Responds to the request with appropriate success and error details. -  https://www.cosmicpython.com/book/chapter_06_uow.html


# Bootstrap and Service
Services isolate all the internal safe happy bits (even the happy modeled errors) from external ugly Internet or message bus or CLI handler concerns.