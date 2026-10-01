# Phase 1 Architecture - AI System

## Goals

- Create a local Mac AI workspace mode for clients, projects, tasks, materials, memory, and improvement insights.
- Keep system rules separate from private workspace data.
- Let AI classify files before any owner-approved movement.
- Build memory as a first-class system component.
- Prepare specs for implementation while stopping before phase 4.

## Boundaries

System-owned repository content:

- `.systems/`
- `.github/`
- `AGENTS.md`
- `HUMANS.md`
- `README.md`
- `.gitignore`

Private local runtime:

- `~/ai-system/ai-system-workspace/`

The local runtime is not committed.

## Components

| Component | Responsibility |
| --- | --- |
| Local mode docs | Define `ai-system` purpose, root, workspace, and operating contract |
| Workspace templates | Generate `core/`, `dump/`, clients, projects, memory, external memory, insights, and skills structure |
| Dump triage | Classify incoming files and prepare owner approval before movement |
| Memory lifecycle | Record raw memory, distillations, checkpoints, reminders, and archives |
| System insights | Store anonymized lessons for owner competence and work quality |
| External memory | Store improvements for the `ai-system` itself |
| Soft integrations | Store links and manual context for Mail, Notion, Google Drive, Notes |
| Validators | Check required README files, privacy boundaries, naming, and workflow artifacts |
| Guide routing | Help owner ask what to do next and trigger dump/distillation/client/project workflows |

## Data Flow

```text
dump/incoming
-> classification artifact
-> owner approval
-> move, copy, or link target
-> index update
-> optional memory entry
-> optional distillation
-> optional anonymized system-insights entry
```

Memory flow:

```text
raw client or project memory
-> distillation
-> checkpoint
-> anonymized system-insights when generally useful
```

## Closed Decisions

- Use `core/` instead of `repo/` in the future local workspace.
- Use `external-memory/` for `ai-system` improvements.
- Use `system-insights/` for owner skill, offer, process, and quality lessons.
- Require anonymization before `system-insights`.
- Start external app context as links and manual imports.
- Require README in every generated directory.
- Defer branch `ai-system` creation until post-final release work.

## Open Decisions

| Decision | Owner | Blocking | Closure Condition |
| --- | --- | --- | --- |
| Exact owner-supplied distillation prompt for promoting memory to system insights | Owner | no | Add prompt before automating promotion |
| Whether future API integrations are needed | Owner | no | Revisit after link-only model proves useful |

## Risks

| Risk | Class | Mitigation |
| --- | --- | --- |
| Private data leaks into `.systems/` | Medium | Add privacy boundary docs and validation |
| AI moves files to the wrong client or project | Medium | Require owner approval before movement |
| Raw memory grows without becoming useful | Medium | Add distillation reminders and checkpoints |
| `system-insights` includes identifiable client facts | Medium | Add anonymization gate and examples |
| External integrations expand into API writes too early | Medium | Keep first implementation link-only |

## Unknowns

### Blocking

None.

### Non-blocking

- Final wording of the owner-supplied distillation prompt.
- Future API integration requirements.
- Final branch creation timing after final owner approval.

## Impact On Project Plan

The project can be planned as a documentation, template, command-routing, and validator change set. The implementation package should avoid real customer data, real file movement execution, and external API access.

