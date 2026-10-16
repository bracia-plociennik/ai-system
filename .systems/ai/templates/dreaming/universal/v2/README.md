# Universal Dreaming v2

Opt-in alongside legacy Dreaming/WEP v1. The reusable product contains no owner configuration.

## Inputs and outputs

`dreaming_config_draft.py` builds an explicit local JSON manifest from supplied workspace identities and source roots. It produces a draft and ownership-gap inventory, never activates anything. Review the concrete sources/owners/recipients before using it. Tasks lacking unambiguous metadata remain gaps; task ownership fields are checked again on every read. Shared task-store location is not company ownership.

`dreaming-cycle inspect --config <absolute-file>` enumerates metadata without model/source body reads. `preflight` checks pinned CLI, auth availability and an actual minimal filesystem namespace, without starting a model. `run --owner-approved` executes only the scheduled window; `--manual` is a separately invoked pilot. The flag acknowledges the manifest's existing scoped authority; it creates no approval.

The report owner is the only owner-report recipient. Other recipients declare proposal/wep adapters and lenses. Source audiences intersect across the ENTIRE analyzer context, including uncited sources: personal context cannot taint technical packets through selective citations. Explicit company-to-private-owner authority is required. No automatic declassification/publication. Model payload sharing additionally requires `model_data_authority` with provider `openai-codex`, scope `one-off` or `recurring`, and a reference to the owner’s explicit approval of this destination; scheduled execution requires recurring scope. A local-data approval alone does not supply this field. A reviewed sanitized source can be registered separately through normal owner approval.

Each generic finding has stable owner/subject/lens/topic identity, kind (keep/improve/stop/try/unknown), labeled claims, actions, cited evidence and full context closure. Source identities preserve paths and hashes; identical bytes count once as independent content. Synthesis consumes evidence-backed findings with their original source closure. It does not reclassify prior reports as fresh raw evidence. Native Work Entry documents may resolve existing WEP identity; no time or readiness approval is inferred. Accepted/rejected/deferred decisions are per recipient and reference an owner decision; no automatic reopening or operational mutation occurs.

Reports, inventory, packets, immutable receipts and completion manifest live only under the selected owner's `dreams/runs/universal-*/`. Source bodies exist only in bounded analyzer batches, not persistent snapshots. Checkpoint hashes bind receipts; source/policy/model/implementation changes invalidate reuse. Unverified historical checkpoints preserve traversal progress but are not current report evidence. Current and historical coverage are separate. Previous legacy reports and pilot receipts remain immutable.

## Runtime

Render the service placeholders `@SYSTEM_HOME@` and `@CONFIG_PATH@` with reviewed absolute local paths. Reject unrendered placeholders before installation. Timer: Thursday/Saturday 02:00 Europe/Warsaw, Persistent=false, no daytime catch-up. Exactly one whole-cycle flock; a slot cannot be replayed implicitly. An interrupted slot resumes its checkpoint evidence in the NEXT scheduled cycle. Cycle budget is 7200 seconds, analysis stops at 6900, 300 seconds reserved for finalization. One transient retry within the SAME deadline, no infinite retry/Restart. systemd also enforces the outer bound and kills the child control group.

Bubblewrap is required on Linux. Unprivileged namespaces must work on the actual host. The analyzer never mounts host workspaces/home/config; it receives approved chunks on stdin, read-only pinned executable/schema and the existing harness authentication mount. Empty ephemeral home disables inherited config/skills/MCP. Shell, apps, plugins, hooks, browser and other execution features are disabled; actual execution/tool events are rejected. Account auth is not copied into reports or product files. A missing isolation/auth/model prerequisite fails closed. Technical logs contain codes/counts only. No cron, fallback host execution, new account, package installation, credentials provisioning, email or chat notification is implied.

## Rollout and rollback

1. Current source-bound focused suites, adversarial/integration review, and required full product release/updater gates.
2. Review owner manifest, task ownership gaps, source inventory and declared sharing. Resolve/model-check supported account and pinned CLI.
3. Host preflight and controlled synthetic then approved private pilot; inspect report assertions and output recipients. Hash source baselines before/after.
4. Product publication/official management updater remain their own approved route; do not copy development scripts into management as a shortcut.
5. Render/install service and timer only at the separate activation boundary. Verify two NATURAL scheduled runs, their completion and privacy/coverage. Do not run extra cycles as a substitute for those dates.
6. Disable/stop the dedicated Dreaming timer/service to pause. Reports, prior configuration and SPOR units remain. No historical report migration or deletion.

Tests use synthetic namespaces and fake analyzers; an actual CLI/host proof is separate from offline fixtures. A code test pass does not prove factual model analysis quality, activation, release, or future natural delivery.
