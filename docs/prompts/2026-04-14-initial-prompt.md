Create domain model first. Discover subdomains. Define bounded contexts. Classify  domains as Core, Generic, or Supporting. Implement Core in the plan for this project. Find and use libraries as-is for supporting and generic domains.

Develop a ubiquitous language. Prepare questions for domain experts. Do reasonable  research first. Identify core domain details that must come from experts, and generic and supporting domain details that should only be confirmed by experts. Use internal knowledge when possible, as many questions have likely already been answered. However, insist on human review of generated requirements.

Summarize the ubiquitous language in a glossary. Refer to the glossary often, and use it to resolve ambiguities before asking. Clearly mark synonymous terms.

The entire domain design does not need to be created up front. It, like all other aspects of software engineering, is subject to change. This includes both further development, refinement, and deprecation over time. However, changes to the domain design should happen at a substantially lower cadence than feature work and bug-fixing tasks.

Describe interfaces in terms of contracts and invariants. Contracts define the format of incoming and outgoing data at the domain's API. Invariants describe states that must hold true at all times at the edges of the API. Invariants may be violated during the processing of a transaction, but their effects must not be visible until the transaction is complete.

Follow the Arrow of Maturity as a project grows. See Arrow of Maturity skills when performing designs. Projects should move quickly from "proof of concept" / Straight Through handler to Domain Model DDD. Projects should extract a repository relatively quickly before production. Introduce aggregates and Unit of Work as those domain operations are discovered. Don't rush to event-sourced microservices, until it is clear the complexity is afforded by the necessity of modeling the dimension of time.