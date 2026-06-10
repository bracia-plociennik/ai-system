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
3. `.systems/ai/core/command-routing.md`.
4. `.systems/ai/core/response-contract.md`.
5. `ai-system-workspace/core/status.md` when present.
6. `ai-system-workspace/dump/` index or classification files when present.
7. Relevant client, owned-asset, or project status files.
8. Relevant memory routers, checkpoint files, distillations, and open decisions.

If an expected artifact is missing, say it is missing and route to creation or recovery.

## Artifact Map

- System rules: `.systems/ai/core/`.
- Workspace status: `ai-system-workspace/core/status.md`.
- Dump inbox: `ai-system-workspace/dump/incoming/`.
- Dump classifications: `ai-system-workspace/dump/`.
- Clients: `ai-system-workspace/clients/`.
- Owned assets: `ai-system-workspace/owned-assets/`.
- Projects: `ai-system-workspace/projects/`.
- Workspace memory: `ai-system-workspace/memory/`.
- External memory for AI System improvements: `ai-system-workspace/external-memory/`.
- Anonymized work-quality lessons: `ai-system-workspace/system-insights/`.
- Owner skills: `ai-system-workspace/skills/`.

## Response Shape

Guide responses must include:

- current status;
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
