# Local Check-In Settings

This is a copyable local-only configuration shape. Do not create a populated configuration automatically and do not commit a private workspace configuration.

```yaml
---
timezone: Europe/Warsaw
private_index_policy_default: detailed-private
---
```

Store an owner-approved populated copy only at `personal-ops/check-ins/check-in-settings.local.md`. It supplies timezone and the default V3 index policy for manual intake, and contains no credentials.

`private_index_policy_default` accepts `detailed-private` or `redacted`. Each canonical V3 report records its effective `private_index_policy`; a later settings change does not rewrite historical index policy.
