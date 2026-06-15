# Skills

This directory stores system-defined AI System skills.

Skills are reusable task-specific guidance for local operations, product maintenance, quality review, skill creation, and other repeatable work.

## Active Skill Layout

Use one directory per active skill:

```text
.systems/ai/skills/<skill-name>/
  context/
  skill-intake-plan.md
  SKILL.md
  README.md
  agents/
  references/
  scripts/
  assets/
  eval-viewer/
```

Only `SKILL.md` and `README.md` are required. Optional directories exist only when they directly support the skill.

`SKILL.md` is the canonical agent contract. It must include frontmatter with only `name` and `description`, plus task guidance, authority boundaries, validation, stop conditions, and output expectations.

`README.md` is a short human-facing overview. It must point to `SKILL.md` and must not duplicate the full operational contract.

Skill names must use lowercase kebab-case.

## Context Intake

`context/` stores raw source material used while creating or updating a skill. It is data only, excluded from normal skill routing, and has no execution authority.

When `context/` exists beside active skill artifacts, `skill-intake-plan.md` is required before final active artifacts are written. The intake plan records reviewed sources, trigger fit, what stays, what is improved or rejected, missing inputs, blockers, artifact mapping, approval state, validation plan, and residual risk.

Do not promote raw source material into `SKILL.md`, `README.md`, or resource files unless it has been reviewed through the intake plan and adapted to the AI System authority boundary.

## User Skills

Local user skills belong under:

```text
AI_SYSTEM_WORKSPACE_HOME/skills/<skill-name>/
  context/
  skill-intake-plan.md
  SKILL.md
  README.md
```

When a user skill and a system skill both match a task, the user skill has priority as local guidance. The system skill remains fallback context.

## Legacy Source Material

External or superseded skill imports can be preserved under:

```text
.systems/ai/skills/legacy/<source-name>/
```

Legacy entries are context/data only. They are not active system skills, are not loaded by skill routing, and may contain source-system conventions that fail current AI System validation.

## Authority

Skills are supporting execution guidance.

They may add stricter procedures, checks, examples, scripts, rubrics, or review criteria.

They must not override `AGENTS.md`, `.systems/ai/core/**`, selected workspace state, privacy rules, owner-approved write gates, evidence, validation, stop conditions, or final acceptance.

When a skill conflicts with a higher-priority source, follow the higher-priority source and record the conflict.
