# Product Capture Binding

Product Capture may explicitly opt into snapshot schema 2 / product-scope-v1,
fresh full-qa-verification-v3 QA and Capture schema 3. This is distinct from the
workspace-only runtime profile. Never relabel historical QA or silently backfill.

The fixed complete product includes .systems/, optional .github/ and required
README.md, HUMANS.md and .gitignore. Entire live namespaces, including untracked
inputs, additions, deletions, bytes and modes, are bound. Optional .github absence
is bound too; creating it invalidates QA. Product namespaces have no caller
exclusions. Unknown tracked paths outside product or ai-workflow-workspace/ reject.
Private/local inputs are not product publication inputs; an actual QA dependency
must be independently included, not hidden behind that publication boundary.

Bind complete external QA dependency directories and individual dependency files
by absolute path, contents, modes and membership. Review semantic source closure:
include the actual installed Workflow policy/validator/template populations,
execution contracts, stable spec/DoD, owner approval and implementation evidence
used by the assessment. Unknown inputs block acceptance. Linked, special, nested
Git, duplicate, overlapping or product-alias dependencies reject. QA and future
closure output cannot bind themselves; bind stable evidence instead.

HEAD is immutable assessed provenance, not a freshness test. Repository and common
Git identities, original provenance commit, full product population and declared
QA dependencies must remain equal. Unrelated runtime commits and index changes
are accepted; product/dependency changes require fresh semantic QA, tests and a
new immutable snapshot/report. Snapshot hashes and QA/Capture references anchor
the selected scope; tampering or changing the assessed HEAD rejects.

This proves current input equivalence only. It does not authenticate every Git
commit or exclude extra staged paths from publication. Exact staging, filtered
publication, full QA/CI/updater tests, owner permission and installed consumers
retain their separate gates. Archived tests are reusable supporting evidence only
after complete input equivalence is independently established; source updates,
CI and updaters still execute fresh. A real Mac/native delivery claim needs its
own evidence, never this binding.

Rollout: review/test/publish the profile via product-publication.md, update the
management consumer officially, then assess the owning product scope and switch
only the explicitly approved Capture proof. Keep all original QA and accepted
distillation byte-identical. Validate the owning collection and unrelated protected
records. No runtime profile migration or SPOR operation is implied.
