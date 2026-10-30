# SilverBullet Tracker Integration

The owner-selected SilverBullet store, local operational tracker and native WEP
ledger have separate responsibilities. Installation, production routing and real
ledger approval each require their actual approved scope. No tax qualification,
bulk migration, task automation, automatic pause or day approval is implied.

## Identity and events

New task creation supplies task_id UUID and created_at UTC. Existing tasks receive
only missing identity on first controlled action; unknown historical dates remain
unknown. Keep IDs through rename. Duplicate identity or conflicted task copies
block use until the owner resolves them. Controlled completion/reopen records
completion/reopen timestamps with event ID and time basis; raw YAML edits do not.
Notes, unknown metadata and checkbox completion undo stay in the native editor.

Every immutable operation has operation_id, device_id, task_id, run_id, action,
occurred_at and expected_version; opening a segment adds segment_id. Replays with
the same content return the saved result. ID reuse with different content fails.
Online only one run is active; explicitly pause/stop it before switching. Stop
leaves task status unchanged. DONE stops its own open run; undo never resumes it.
SQLite stores operational state, versions, conflicts and transaction receipts.
Active segments use UTC instants, partitioned at Europe/Warsaw midnight including
23/25-hour days. Pauses contribute no duration. Restart/invalid clocks need review.

## Native offline client

Embed templates/workspace/tasks/silverbullet-tracker-ui.mjs with the native panel.
The io(operation, JSON payload) callback provides list/read/write through Space
API, plus identity/current guarded native-editor reads/edits. Only tracker-outbox/,
tracker-acks/, tracker-cache/ and tracker-drafts/ pages may be accessed by this
bridge. Each immutable outbox event has its own page; acknowledgements are separate.
Only the random device identity uses localStorage. Private task/event/draft content
uses the native Space store, synchronization and the owner's encryption settings.
Native encryption is not enabled or changed by the tracker.

The UI distinguishes local pending and confirmed state. Reconnect replays the
outbox. Out-of-order or multi-device stale events are preserved as conflicts;
stop affected active runs, then manually resolve with explicit per-day time and
reason or exclude the run while retaining history. Conflicts block WEP approval.
Offline time and corrections require owner confirmation; original segments remain.

## Service boundary

Run scripts/silverbullet-tracker --config /absolute/owner-config.json as the owner
account, with no public TCP listener. Config has workspace, socket_path, origin,
allowed_user, native_url (http://127.0.0.1:PORT only), optional evidence_level
(production-readback normally, local-test only for isolated fixtures). Expose only
/.task-tracker/api/v1/* and the existing create-only /.task-create/* via Caddy's
Unix-socket reverse proxy. Keep native Shell and Runtime APIs disabled.

For each request the adapter checks the existing session against the pinned
SilverBullet 2.12.1 /.dashboard/api/profile and configured owner/admin identity.
Mutations require exact Origin and session-bound X-Task-Tracker-CSRF obtained from
GET /state. Cross-origin calls, generic paths, redirects and oversized bodies are
rejected. Create-only PUT retains If-None-Match: * and native X-Sync-Mode headers,
adds true creation identity, and never overwrites an existing task.

GET /state exposes timer version, runs, event history, drafts and registry choices.
POST /events accepts {event, replay}; POST /wep/preview builds a hashed preview;
POST /wep/approve accepts exactly {preview_id, preview_hash}. POST /wep/refresh
retries workbook export for a committed preview. Expired sessions preserve pending
native events but cannot approve WEP.

Harden the systemd service: no privilege escalation, private temporary directory,
read-only product source and only necessary task/source/config paths, writable
vault/work-evidence/socket paths. Hide private tax, credentials and unrelated
workspaces. Give Caddy access only to the runtime socket directory, never WEP.
Do not put credentials/session cookies in config, logs or product sources.

## Explicit WEP approval and recovery

Stop opens a partial draft; DONE proposes done. Require the result of work and
explicit registry client/project selection or confirmed missing attribution. Show
active segments, dates, original measurement, correction/reason and evidence.
Preview alone never writes work entries. Measured online segments remain measured;
offline/corrected time is owner-confirmed with its source and original retained.

The stable task_ref silverbullet:UUID maps to a stable task grouping work_id.
Native WEP requires one work_id per entry, so run pieces receive deterministic
child refs/IDs under that grouping. Historical bindings remain untouched. Never
weaken native work-ID uniqueness or reinterpret historical entries.

Approval pins task content, tracker version, registry/ledger snapshot, source hashes
and exact preview hash. Changed inputs require a new preview. A detached immutable
receipt records the actual approval click before native prepare/apply. Persist
prepared transaction coordinates before apply; retry/recovery uses the same native
transaction and committed manifest, avoiding duplicate work. The WEP ledger remains
the authority for approved work. Export time-tracker.xlsx afterwards with native
Manual Inputs preservation. Export failure keeps the committed entry and a visible
pending-refresh receipt; refreshing never repeats the ledger write.

Rollback restores the previous native panel/routing and disables the service;
retain SQLite, native events, approval receipts and committed WEP. Do not remove
history or bulk-rewrite task IDs as part of deployment/rollback. Test against an
isolated owner fixture; production verification must not create demo work entries.
