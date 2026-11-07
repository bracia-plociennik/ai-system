# Chat-led Dreaming

This optional successor to the batch executor performs analysis in one existing,
explicitly selected private owner chat. The scheduler only prepares approved data,
queues the prompt and verifies checkpoints/report delivery. It never calls a model
subprocess or performs recommendations. Activation requires exact owner scope,
current QA, a real manual pilot and verified standard owner settings.

`dreaming_chat.py begin|accept|finalize|inspect --config <v2-registry>` owns the
guarded snapshot, cumulative checkpoint and private report. `begin --manual` gets
a unique cycle; the scheduled cycle uses Wednesday/Saturday02:00 Europe/Warsaw.
A restart retains its cycle and original deadline. New slots inherit pending
history without copying old run directories. Preparing data is not reviewing it:
coverage advances only from validated model review declarations, not byte counts.
Within one cycle, cumulative findings have unique stable topic/lens keys and retain
earlier facts and evidence IDs verbatim. Valid evidence may expand owners/subjects
and therefore recompute global protocol IDs without losing the logical finding.
Summaries, interpretations, unknowns and proposals may be refined; provenance and
owner-only privacy are validated afresh, with no transfer of recipient approvals.
Trusted state stores shared context references/sets once and verifies their hashes
when loading; model checkpoint JSON cannot inject that internal representation.
The initial pass prioritizes the last seven days without excluding older material.
Later passes distinguish new/changed files from known backlog using a saved
inventory, and select chunks across registered roots to avoid source starvation.

`dreaming_chat_dispatch.py --config <private-controller.json>` reuses an explicitly
hash-pinned SPOR transport; it does not modify SPOR. `--manual` requests a pilot;
`--resume` reconciles an existing reserved/native turn rather than resubmitting it.
One controller lock covers the full session. Scheduled input expires at03:00,
without daytime catch-up. Two hours includes analysis and reserved finalization.
Only the controller's own turn may be interrupted on deadline/failure.

The controller requires the existing Approve for me mode: workspace-write,
on-request and auto_review, with the configured model. It never writes configuration,
creates/selects a permission profile or changes/restores thread settings. A read-only
native settings check and harmless built-in workspace command canary precede input;
settings drift stops further acceptance. Actual model tools must succeed in the pilot.
Source Guard and credential screening prepare the approved manifest. The analyst's
instructions restrict knowledge analysis to these inputs, forbid dereferencing raw
source paths and forbid connectors/network and recommendation execution. Mandatory
startup/policy reads are allowed. The default workspace sandbox can read more than the
manifest: this mode does not claim OS read isolation, credential invisibility or an
equivalent replacement for the batch executor's namespace boundaries.

Private controller schema2 uses mode=approve-for-me; obsolete profile_id configuration
is rejected. Native queue auto-consumption can precede persisted history readback.
After queue/start is busy or its response is lost, bounded client-ID polling reconciles
the original submission without re-adding it. An unresolved delivery stays uncertain,
blocks automatic replay/continuation and needs operator reconciliation. Cancellation
interrupts only a proven own turn and never changes the owner's settings.

The controller validates schema, evidence IDs, source/config freshness and
credential markers. The resulting report remains owner-private, including all
technical suggestions. It does not imply semantic truth, recipient acceptance,
work evidence, time spent, memory promotion or permission to execute actions.
Old decisions and historical QA remain immutable. Unsupported, blocked, pending,
changed and reviewed materials remain distinct. Retired manifest scopes never
re-enter through cache reuse. Attachments/OCR/unreviewed exports remain excluded.

Run `check-dreaming-chat`, existing Dreaming/WEP and SPOR regressions, native
standard-mode checks and queue failure controls, then required full release/updater checks with smoke. A
completed session can still leave historical backlog. Two actual natural terms
are required after activation; a manual pilot cannot satisfy those observations.

## Cross-cycle logical replacement and decisions

The chat cache uses topic/lens as the logical replacement key, while native global
IDs retain recomputed owner/subject provenance. Before a new brief, each cached
context and evidence version must match the guarded snapshot; stale or ambiguous
legacy cache groups are omitted, never silently relabeled as current. Finalization
checks each reference version against one fresh read per locator; a later version
cannot mask an older hash. Uncited read context and within-cycle drift remain
conservative invalidation dependencies.

Trusted owner-private identity lineage preserves recipient-local owner decisions
when provenance rekeys a finding. Conflicting aliased decisions fail closed;
aliases never transfer approvals to technical recipients. Model checkpoints cannot
supply aliases. Lineage can survive an analyzer/code cache reset only under the
same explicit owner/source manifest; content reuse still requires the full scope
binding. Historical reports and decisions remain unchanged. Superseded findings
and stale-before-cycle cache disposition are reported separately. Legacy cache
without a matching decision-scope binding supplies no cross-scope alias authority.
A legacy/reset cache with existing owner decisions and no verifiable lineage
scope blocks preparation pending explicit reconciliation instead of reopening
rejected work under a changed global ID. No decision is guessed or migrated.

## Multiple batches within the original native turn

The initial brief is a bounded batch, not the cycle's full analysis allowance.
After reviewing it, the main-chat analyst saves a cumulative nonfinal checkpoint
and calls `dreaming_chat.py next-batch --config ... --cycle ... --after-batch N`.
This deterministic Source Guard command extends only the same cycle and writes a
new brief; no model/network process, new turn, source enrollment or deadline reset.
The analyst reads every newly prepared chunk, preserves earlier findings/facts and
evidence verbatim, and repeats until exhausted or time-budget, reserving synthesis.
Batch numbers reconcile lost replies without preparing a second batch. Unreviewed
inputs cannot be advanced. Source/config/implementation changes stop preparation;
no source version is silently replaced. The controller reloads trusted batch state
before accepting checkpoints. Original snapshots/reports and terminal cycles stay
immutable. Global coverage counts complete files, not fragments or registry roots.
`completed` describes synthesis of actual reviewed scope; pending archive remains
explicit. Only the helper may dereference registered original paths in this stage.
