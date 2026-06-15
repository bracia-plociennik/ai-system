# Guide

## Purpose

Guide mode helps the owner recover orientation, resume safely, and choose the next action.

Use it when the owner says:

- `co teraz`;
- `co dalej`;
- `zgubiłem się`;
- `jak zacząć`;
- `what should I do next`.

## Required Reads

Read the smallest set needed to answer safely:

1. `AGENTS.md`; if it is missing, use `.systems/ai/templates/root/AGENTS.template.md` only to recommend local initialization with `.systems/scripts/init-ai-system`.
2. `.systems/ai/core/operating-model.md`.
3. `.systems/ai/core/workspaces.md`.
4. `.systems/ai/core/command-routing.md`.
5. `.systems/ai/core/project-state.md` when project state or project repositories are relevant.
6. `.systems/ai/core/prompt-composition.md` when prompting artifacts are relevant to the answer.
7. `.systems/ai/core/response-contract.md`.
8. `ai-system-workspaces.md` when present.
9. Selected workspace `core/status.md` when present.
10. Selected workspace `dump/` index or classification files when present.
11. Relevant primary-entity, client, owned-asset, or project-state status files in the selected workspace.
12. Relevant memory routers, checkpoint files, distillations, and open decisions.
13. Relevant accepted prompting artifacts after the status, memory, decision, and checkpoint artifacts they reference.
14. Relevant selected-workspace skill `SKILL.md`, then relevant system skill `SKILL.md`, when a matching skill exists.

If an expected artifact is missing, say it is missing and route to creation or recovery.

## Artifact Map

- System rules: `.systems/ai/core/`.
- Workspace registry: `ai-system-workspaces.md` when present.
- Workspace status: `<workspace>/core/status.md`.
- Workstreams: `<workspace>/core/workstreams.md`.
- Dump inbox: `<workspace>/dump/incoming/`.
- Dump classifications: `<workspace>/dump/`.
- Clients: `<workspace>/clients/`.
- Primary entity: `<workspace>/status.md` and `<workspace>/memory.md` when the selected workspace uses a primary-entity root.
- Owned assets: `<workspace>/owned-assets/` in generic workspaces or explicit sub-asset namespaces.
- Projects and source folders: `<workspace>/projects/`.
- Project state: `<workspace>/project-state/`.
- Workspace memory: `<workspace>/memory/`.
- External memory for AI System improvements: `<workspace>/external-memory/`.
- Anonymized work-quality lessons: `<workspace>/system-insights/`.
- Prompting: `<workspace>/prompting/`, `<workspace>/clients/<client>/prompting/`, `<workspace>/clients/<client>/projects/<project>/prompting/`, and `<workspace>/projects/<project>/prompting/`.
- Owner skills: `<workspace>/skills/<skill-name>/SKILL.md`.
- System skills: `.systems/ai/skills/<skill-name>/SKILL.md`.

## Response Shape

Guide responses must include:

- current status;
- selected workspace and selection source;
- sources checked;
- blockers or unknowns;
- exactly one recommendation with impact;
- exactly one safe alternative with impact;
- copy-paste prompts for both paths.

The `Co dalej?` footer from `.systems/ai/core/response-contract.md` can serve as the recommendation and alternative section.

## Drift And Conflict Handling

If filesystem state, status, memory, checkpoint, or owner request conflict, do not guess.

Recommend reconciliation first, for example:

```text
Porównaj status, dump, memory, checkpointy i pliki projektu. Nie zapisuj nic. Powiedz, od którego punktu można bezpiecznie kontynuować.
```

If the owner wants speed, the safe alternative may be a narrower read-only status check.

## Blockers

Guide mode must stop before recommending execution when:

- active client or project is unknown;
- target file ownership is ambiguous;
- required evidence is missing;
- material may contain secrets, legal content, or private customer data;
- requested writes lack `owner-approved`;
- real external effects would be needed;
- the request bypasses privacy, approval, or validation.

The recommendation should resolve the highest-impact blocker.
