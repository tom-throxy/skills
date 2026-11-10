# Data and schema design

Load when the change adds or alters tables, columns, indexes, migrations, document shapes, stored file formats or cache keys.

Schemas are one-way doors: once data is written in a shape, changing it costs a migration. Question these deeply.

- **Queries first**: list the reads and writes this data will serve, with rough frequency. The schema should fit those queries. A schema designed without them is a guess.
- **Normalisation**: normalise by default. Denormalise only for a measured or clearly expected read-path need, and then say what keeps the copies in sync. Watch for **dual writes** (two stores updated without a transaction) and **update anomalies**.
- **Shape smells**: **god table** (one table everything joins to and every feature adds columns to); **entity-attribute-value** (generic key/value rows instead of real columns); **polymorphic association** without integrity; JSON columns hiding fields that are queried or filtered on.
- **Invariants**: are rules enforced by the database (`NOT NULL`, foreign keys, unique and check constraints), or only by application code that some future path will skip?
- **Indexes**: does every hot query have an index that serves it? Does every new index earn its write cost? Is a uniqueness rule backed by a unique index, not a read-then-write race?
- **Migration safety**: will it lock a large table? Does it need a backfill, and can that run online in batches? Can the previous app version run against the new schema during deploy? Use **expand-contract** for renames and type changes. Is there a rollback?
- **Lifecycle**: retention, deletion, archival. Personal data: where it is stored, who can read it, and how it is erased on request. Soft deletes: does every query filter them out?
- **Source of truth**: is this data owned here, or copied from somewhere else? If copied, what reconciles drift?
- **Growth**: how many rows per tenant, per day, in a year? Does anything need partitioning or a time-based cleanup before then?
- **Time and money**: timestamps stored in UTC with a time zone type; money stored as integer minor units or decimal, never float; currency stored alongside.
