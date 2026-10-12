# WEP-CONTENT-008 Implementation
Source/DoD: specs/phase-3-wep-content-008-editorial-drafts-specification.md.
## Implementation Slice Plan
| slice id | goal | expected files/areas | acceptance check | evidence required | status |
| --- | --- | --- | --- | --- | --- |
| content-1 | Source/privacy/claim bundle | module/core/template | safe current facts; holds and anonymization | adversarial fixtures | completed |
| content-2 | Brand cadence/draft review | module/CLI/template | distinct voices, bound approvals, variant capacity | two-brand normal/failure traces | completed |
| content-3 | Full review | tests/private QA | no publication or unsupported benefits | regression and artifact QA | completed |
Stop if publication, private tax ingestion, unapproved source or real API needed.
## Instruction Refresh
Current full refresh and task-specific accepted spec/plan/predecessor interfaces;
baseline bcd1e0d with only approved product/private changes.
## Delivery Constraints
Owner-opt-out no deadline/timebox; privacy/evidence/QA preserved.
## Distillation State
Work ID: WEP-CONTENT-008-editorial-drafts; State: ready.
## Slice Execution Evidence
Current module, CLI, core contract and editorial template reviewed against full
specification. Eleven editorial tests plus full regression: 124 executions,
exit0. Counts include inherited fixtures and are not unique test counts.
Manual two-brand trace produced Polish first-person and English company
newsletters plus linked socials; Markdown line breaks and escaping inspected.
Queue: 28 slots over four weeks, language variants share slots, no publishing.
Private filesystem hashes unchanged by preview; approved local persist wrote
four files and retry preserved all bytes. Unsupported source stopped with
held-or-missing-claim. Source/translation drift, combined identifiers, secret
canaries and missing documentation block output. All derivatives need review.
Pre-quality source inspection caught literal backslash-n formatting; corrected
inside this slice before tests, no failed acceptance hidden. Unknown claim
tokens now fail closed. No real brand/source or publication used in tests.
## Owner Decision Checkpoint
Clear for synthetic drafts; real recipients/publication not authorized.
## Optional Knowledge Capture
Required project phase6 after scoped Quality.
## Model Recommendation
High reasoning, privacy and claim integrity; Blocking: no.
