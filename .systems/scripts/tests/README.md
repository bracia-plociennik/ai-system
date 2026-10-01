# Integrity Regression Tests

Offline synthetic fixtures for validation lifecycle, evidence ownership, eval freshness,
scope completeness, skill metadata and updater relations. Run `check-validation-integrity`.
No private runtime, external model sessions or network remotes are used.
Fixture tests also verify complete per-domain physical copies, metadata equivalence,
mutation independence and rejection before copy for unsafe sources/destinations.
Bounded transaction tests verify seven separate roots/processes, concurrency no
greater than two, failure propagation, draining of the started peer, and absence
of writes from later transactions after a failed pair.
