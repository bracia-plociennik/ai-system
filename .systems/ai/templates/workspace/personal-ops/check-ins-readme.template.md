# Daily Check-Ins

## Purpose

Canonical Markdown records for daily check-ins.

Each day lives at:

```text
AI_SYSTEM_WORKSPACE_HOME/personal-ops/check-ins/YYYY/YYYY-MM-DD.md
```

## Rules

- One Markdown file per check-in day.
- Frontmatter stores structured fields.
- Body sections store reflection text.
- Empty source values stay empty; do not invent check-in values.
- Raw Notion exports remain in `dump/incoming/external/notion/check-ins/` until owner-approved cleanup.
- Index files in `personal-ops/indexes/` are derived artifacts. Markdown wins if they disagree.

## Privacy

Daily check-ins are `private-sensitive` by default.
