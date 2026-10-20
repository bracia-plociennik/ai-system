# Chat-led Dreaming

This optional successor to the batch executor performs analysis in one existing,
explicitly selected private owner chat. The scheduler only prepares approved data,
queues the prompt and verifies checkpoints/report delivery. It never calls a model
subprocess or performs recommendations. Activation requires exact owner scope,
current QA, a real manual pilot and tested native permission enforcement.

`dreaming_chat.py begin|accept|finalize|inspect --config <v2-registry>` owns the
guarded snapshot, cumulative checkpoint and private report. `begin --manual` gets
a unique cycle; the scheduled cycle uses Wednesday/Saturday02:00 Europe/Warsaw.
A restart retains its cycle and original deadline. New slots inherit pending
history without copying old run directories. Preparing data is not reviewing it:
coverage advances only from validated model review declarations, not byte counts.

`dreaming_chat_dispatch.py --config <private-controller.json>` reuses an explicitly
hash-pinned SPOR transport; it does not modify SPOR. `--manual` requests a pilot;
`--resume` reconciles an existing reserved/native turn rather than resubmitting it.
One controller lock covers the full session. Scheduled input expires at03:00,
without daytime catch-up. Two hours includes analysis and reserved finalization.
Only the controller's own turn may be interrupted on deadline/failure.

The named permission profile denies host reads by default, permits minimal runtime
and the exact Codex executable, reads only the screened session input directory
and writes only its draft directory. Network is disabled; credential environment
variables fail preflight. Source roots, previous snapshots, trusted control state,
auth/config files and app-server socket are unavailable to model commands. A real
native `command/exec` negative-control probe must pass before any private input is
submitted. Generic readOnly is not equivalent and is never a fallback.

The controller validates schema, evidence IDs, source/config freshness and
credential markers. The resulting report remains owner-private, including all
technical suggestions. It does not imply semantic truth, recipient acceptance,
work evidence, time spent, memory promotion or permission to execute actions.
Old decisions and historical QA remain immutable. Unsupported, blocked, pending,
changed and reviewed materials remain distinct. Retired manifest scopes never
re-enter through cache reuse. Attachments/OCR/unreviewed exports remain excluded.

Run `check-dreaming-chat`, existing Dreaming/WEP and SPOR regressions, native
permission controls, then required full release/updater checks with smoke. A
completed session can still leave historical backlog. Two actual natural terms
are required after activation; a manual pilot cannot satisfy those observations.
