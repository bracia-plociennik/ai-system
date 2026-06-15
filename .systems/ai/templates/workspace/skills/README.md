# User Skills

User-defined local skills belong here.

Preferred layout:

```text
AI_SYSTEM_WORKSPACE_HOME/skills/<skill-name>/
  context/
  skill-intake-plan.md
  SKILL.md
  README.md
```

`SKILL.md` is the canonical agent contract. `README.md` is a short human-facing summary.

When a user skill and a system skill both match a task, the user skill has priority as local guidance.

`context/` stores raw source material for skill creation or updates. It is not normal skill guidance and has no execution authority.

When `context/` exists beside `SKILL.md`, `README.md`, or resource directories, create `skill-intake-plan.md` from `skill-intake-plan.template.md` before writing final active artifacts.

User skills can guide AI locally but cannot override `AGENTS.md`, `.systems/ai/core/**`, selected workspace status, privacy rules, owner-approved write gates, validation, evidence, stop conditions, or final acceptance.
