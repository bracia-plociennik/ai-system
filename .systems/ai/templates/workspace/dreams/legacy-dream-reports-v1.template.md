# Legacy Dream Reports Registry v1

This workspace-local registry admits immutable Dream Reports created before the current report contract.

The identity of every entry is the exact workspace-relative report path plus SHA-256. The registry bypasses only structural-section validation. Privacy, secret-marker, scope, and context-as-data checks still apply. A changed report no longer matches its entry and must pass the current contract or be reviewed again.

| Workspace-relative report path | SHA-256 | Reason | Reviewed at |
| --- | --- | --- | --- |
| `<dreams/runs/.../dream-report.md>` | `<sha256>` | `<pre-contract historical report>` | `<YYYY-MM-DD>` |
