# API design

Load when the change adds or changes an HTTP, RPC, GraphQL, SDK or library interface that other code or other teams call.

Design from the caller's side first: write the call the consumer will actually make, then check the server shape serves it.

- **Invocation**: how will callers really use this? How many calls does a common task take? A task needing three sequential calls is a **chatty API**. One endpoint that does everything behind flags is a **god endpoint**.
- **Resource modelling**: are nouns and verbs consistent with the rest of the API? Does the URL or type name say what the thing is, rather than how it is stored?
- **Idempotency**: can a retried create or payment be repeated safely? Mutations that matter need an **idempotency key** or natural idempotency.
- **Errors**: is the error shape consistent with the existing API? Can callers tell retryable from permanent failures? Are status codes honest (no 200 with an error body)?
- **Collections**: is anything returning an unbounded list? Use pagination, preferably **cursor-based** for data that changes.
- **Evolvability**: can fields be added without breaking callers? Are required fields truly required? Is a breaking change versioned or run as **expand-contract**? Remember **Hyrum's law**: field order, default values and timing all become contracts.
- **Boundary**: does the API leak internal structure (database ids, table shapes, internal enums) that will freeze the internals? That is a **leaky abstraction** and makes the schema a one-way door.
- **Authorisation**: is permission checked at the boundary for every operation, including reads of related objects?
- **Consistency**: does it follow the conventions already in this codebase (naming, casing, envelope, auth), even where you would choose differently?
