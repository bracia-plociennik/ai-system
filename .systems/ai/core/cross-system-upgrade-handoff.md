# Cross-System Upgrade Handoff

## Purpose

Keep substantive AI System and AI Workflow upgrades intentionally aligned without automatic cross-repository writes.

This contract applies to system-maintenance upgrades that may be useful in the counterpart system. It does not apply to ordinary product, client, project, or domain work.

## Required Decision

Before commit or handoff, record:

```text
Cross-system impact:
- Owner decision: <yes|no|pending>
- Counterpart: <ai-workflow|ai-system|none>
- Handoff artifact: <path|not-required|pending>
- Reason:
```

- `yes`: create one privacy-safe External Memory handoff for the complete accepted scope;
- `no`: use `Counterpart: none` and `Handoff artifact: not-required`, with a short reason;
- `pending`: stop before commit and handoff.

The owner decides shared impact for every substantive system upgrade. A no-question opt-out, plan acceptance, or model recommendation cannot infer or auto-resolve the decision.

## Handoff Location

The handoff lives in the selected workspace:

```text
AI_SYSTEM_WORKSPACE_HOME/external-memory/memory/<date>-<topic>-<counterpart>-handoff.md
```

Existing files directly under `external-memory/` remain valid historical AI System improvement entries. This contract does not migrate, rename, or rewrite them.

Use `.systems/ai/templates/capture/cross-system-upgrade-handoff.template.md`.
For a tracked decision record, use `external-memory/memory/<file>.md` relative to the selected workspace. Validate it with `--workspace` so local home paths are not published; absolute paths remain accepted for local-only records.

## Handoff Requirements

The handoff contains:

- concept and intended outcome;
- owner decisions;
- safety and authority boundaries;
- source-system reference paths;
- validators and smoke-test expectations;
- counterpart adaptation checklist;
- privacy/scope check;
- residual risk.

Do not include raw client data, client names, people names, private company names, domains, secrets, credentials, production identifiers, project-specific runtime, or copied private repository content.

## Producers And Consumers

Producers:

- a substantive AI System or AI Workflow system-maintenance plan;
- a pre-commit or handoff response;
- an owner-approved handoff capture.

Consumers:

- contract compliance before commit or handoff;
- External Memory handoff creation when the decision is `yes`;
- later counterpart idea validation and adaptation.

## Authority Boundary

The decision and handoff are advisory for the counterpart. They do not:

- grant write, commit, push, deployment, migration, or approval authority;
- change source-of-truth order, privacy, risk, permissions, Definition of Done, QA, evidence, stop conditions, or owner approvals;
- automatically modify the counterpart system;
- turn External Memory into project, client, or product-domain memory.
