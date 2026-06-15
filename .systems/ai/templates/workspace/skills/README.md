# User Skills

User-defined local skills belong here.

Preferred layout:

```text
AI_SYSTEM_WORKSPACE_HOME/skills/<skill-name>/
  SKILL.md
  README.md
```

`SKILL.md` is the canonical agent contract. `README.md` is a short human-facing summary.

When a user skill and a system skill both match a task, the user skill has priority as local guidance.

User skills can guide AI locally but cannot override `AGENTS.md`, `.systems/ai/core/**`, selected workspace status, privacy rules, owner-approved write gates, validation, evidence, stop conditions, or final acceptance.
