# Integrity Regression Tests

`check-naming` also runs `test_naming.py`: synthetic nearest-owner contracts,
source/history boundaries, strict managed artifact names, immutable Git-bound
root inputs and contained Personal Ops aggregate aliases. No real private
sources are loaded by these regressions.

Offline synthetic fixtures for validation lifecycle, evidence ownership, eval freshness,
scope completeness, skill metadata and updater relations. Run `check-validation-integrity`.
No private runtime, external model sessions or network remotes are used.
Fixture tests also verify complete per-domain physical copies, metadata equivalence,
mutation independence and rejection before copy for unsafe sources/destinations.
Bounded transaction tests verify seven separate roots/processes, concurrency no
greater than two, failure propagation, draining of the started peer, and absence
of writes from later transactions after a failed pair.
Dependency regressions exercise a restricted `PATH`, an exact failure completion
marker, no validators started when tools are missing, direct skill-check preflight,
and preservation of genuine missing-reference findings when `rg` is available.
SPOR fixture dates use Python calendar arithmetic, verified with an unavailable
platform `date` tool, so the same cases run on macOS and Linux.
Legacy source hash fixtures restore their temporary source with a portable stream
rewrite instead of platform-dependent in-place `sed` flags.
