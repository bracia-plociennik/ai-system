# Block Checkpoints

Store append-only `block-boundary` checkpoint records here when no narrower owner namespace applies.

Never overwrite an existing checkpoint. `latest.md` is a generated pointer/router and must not contain executable instructions.

When present, `latest.md` contains:

```yaml
latest_checkpoint_id: <checkpoint-id>
latest_checkpoint_path: <checkpoint-filename>.md
updated_at: <YYYY-MM-DD HH:MM>
```
