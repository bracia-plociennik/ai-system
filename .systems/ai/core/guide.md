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

1. `AGENTS.md`.
2. `.systems/ai/core/operating-model.md`.
3. `.systems/ai/core/workspaces.md`.
4. `.systems/ai/core/command-routing.md`.
5. `.systems/ai/core/response-contract.md`.
6. `ai-system-workspaces.md` when present.
7. Selected workspace `core/status.md` when present.
8. Selected workspace `dump/` index or classification files when present.
9. Relevant client, owned-asset, or project status files in the selected workspace.
10. Relevant memory routers, checkpoint files, distillations, and open decisions.

If an expected artifact is missing, say it is missing and route to creation or recovery.

## Artifact Map

- System rules: `.systems/ai/core/`.
- Workspace registry: `ai-system-workspaces.md` when present.
- Workspace status: `<workspace>/core/status.md`.
- Workstreams: `<workspace>/core/workstreams.md`.
- Dump inbox: `<workspace>/dump/incoming/`.
- Dump classifications: `<workspace>/dump/`.
- Clients: `<workspace>/clients/`.
- Owned assets: `<workspace>/owned-assets/`.
- Projects: `<workspace>/projects/`.
- Workspace memory: `<workspace>/memory/`.
- External memory for AI System improvements: `<workspace>/external-memory/`.
- Anonymized work-quality lessons: `<workspace>/system-insights/`.
- Owner skills: `<workspace>/skills/`.

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
