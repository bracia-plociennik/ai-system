# Phase 2 Project Plan - AI System

## Plan Result

`PASS`

## Task Sequence

| Task ID | Goal | Risk | Readiness | User Decision Before Implementation |
| --- | --- | --- | --- | --- |
| `ASYS-CORE-001-local-ai-system-mode` | Define local mode, paths, and branch policy | Medium | ready | no |
| `ASYS-WORKSPACE-002-workspace-layout-templates` | Add local workspace templates and README contracts | Medium | ready | no |
| `ASYS-DUMP-003-dump-triage-owner-approval` | Define dump classification and approval flow | Medium | ready | no |
| `ASYS-MEMORY-004-memory-lifecycle` | Define memory, distillation, checkpoint, and reminder lifecycle | Medium | ready | no |
| `ASYS-INSIGHTS-005-system-insights-anonymization` | Define insights routing and anonymization gate | Medium | ready | no |
| `ASYS-CLIENT-006-client-project-workspaces` | Define client and project workspace layouts | Medium | ready | no |
| `ASYS-LINKS-007-soft-integrations` | Define link-based external context model | Low | ready | no |
| `ASYS-GUIDE-008-guide-command-routing` | Add guide and command routing for local workspace work | Medium | ready | no |
| `ASYS-VALIDATION-009-validators-quality` | Add validators for README and privacy boundaries | Medium | ready | no |
| `ASYS-DOCS-010-human-runbook-examples` | Add human docs and examples | Low | ready | no |

## Dependencies

- `ASYS-CORE-001` must come first because later tasks depend on the mode and path model.
- `ASYS-WORKSPACE-002` depends on `ASYS-CORE-001`.
- `ASYS-DUMP-003`, `ASYS-MEMORY-004`, and `ASYS-INSIGHTS-005` depend on the workspace layout.
- `ASYS-CLIENT-006` depends on memory and workspace layout.
- `ASYS-LINKS-007` depends on client and project layouts.
- `ASYS-GUIDE-008` depends on the operating model and core workflows.
- `ASYS-VALIDATION-009` depends on the generated layout and routing rules.
- `ASYS-DOCS-010` finishes the human-facing guide after all contracts are known.

## Definition Of Done

- Local mode is documented.
- Workspace templates define every required directory and README.
- Dump triage blocks file movement without owner approval.
- Memory lifecycle and distillation reminders are documented.
- `system-insights` is separated from `external-memory`.
- Anonymization gate is documented.
- Soft integrations are link-based only.
- Validators cover required README files and privacy boundaries.
- Human docs include usage examples.
- Phase 4 is not started by autopilot.

## Post-final Release Work

Create or move the completed variant to branch `ai-system` only after final check and owner approval.

