# Micro-Project: `dreaming-mode-v1`

## Summary

Dodajemy advisory-only `Dreaming Mode`: tryb nocnej / AFK analizy, który tworzy raport rekomendacji w `AI_WORKFLOW_WORKSPACE_HOME/dreams/`, bez automatycznego promowania czegokolwiek do memory, System Insights, External Memory, skills, statusu ani repo source.

V1 ma dwa jawne warianty:
- `workflow-artifacts-only` - skanuje tylko artefakty AI Workflow workspace.
- `full-repo` - skanuje artefakty workflow oraz repo/kod pod kątem review candidates, wzorców i braków.

V1 nie implementuje schedulera. Uruchomienie odbywa się ręcznie przez prompt/guide, a późniejsza automatyzacja może powstać jako osobny micro-project.

## Key Changes

- Dodać core policy `dreaming-mode.md` opisującą:
  - tryb `advisory-only`;
  - warianty `workflow-artifacts-only` i `full-repo`;
  - dozwolone źródła dla każdego wariantu;
  - zakazane działania: commit, push, status mutation, durable memory write, System Insight write, External Memory write, skill creation, destructive commands, production/external effects;
  - privacy boundary: nie kopiować sekretów, `.env`, client raw data, nazw klientów, danych produkcyjnych ani prywatnych identyfikatorów.
- Dodać workspace namespace:
  ```text
  AI_WORKFLOW_WORKSPACE_HOME/dreams/
    README.md
    runs/
      YYYY-MM-DD-<slug>/
        dream-report.md
  ```
- Dodać report template z wymaganym polem:
  - `Dream variant: <workflow-artifacts-only|full-repo>`
- Report template zawiera sekcje:
  - source inventory;
  - workflow artifact findings;
  - repo/code review findings, wymagane tylko dla `full-repo`;
  - memory promotion candidates;
  - External Memory candidates;
  - System Insights candidates;
  - skill candidates;
  - things to improve/remove;
  - missing capabilities;
  - rejected as noise;
  - privacy/scope check;
  - owner decision queue.
- Routing:
  - `dreaming mode`, `nightly analysis`, `AFK review`, `scan dreams` domyślnie route do `workflow-artifacts-only`;
  - `full repo dreaming`, `dreaming full repo`, `scan repo in dreaming mode` route do `full-repo`;
  - output tylko w `AI_WORKFLOW_WORKSPACE_HOME/dreams/runs/**`;
  - każdy kandydat musi mieć source path, reason, target, risk/privacy note i owner action.
- Docs:
  - zaktualizować `AGENTS.md`, `HUMANS.md`, `workflow.md`, `memory.md`, `system-insights.md`, `contract-compliance.md`, `commands.md`, `installation.md`, `update-from-upstream.md`;
  - opisać różnicę między Dream Report a durable memory;
  - dopisać, że scheduler/automation jest out of scope V1.
- Workspace bootstrap:
  - `init-workspace` i `update-workspace` mają idempotentnie tworzyć tylko brakujące neutralne `dreams/README.md` i `dreams/runs/`;
  - nie nadpisywać istniejących dream reports.

## Validators And Smoke Tests

- Dodać `.systems/scripts/check-dreaming-mode`.
- Validator sprawdza:
  - core policy, templates, workspace README i docs references istnieją;
  - oba warianty są udokumentowane;
  - report template zawiera `Dream variant: <workflow-artifacts-only|full-repo>`;
  - `workflow-artifacts-only` nie wymaga repo/code review findings;
  - `full-repo` wymaga repo/code review findings;
  - report template zawiera privacy/scope check;
  - wording nie pozwala na automatyczne durable writes do memory/system-insights/external-memory/skills/status;
  - dream reports w workspace, jeśli istnieją, nie zawierają typowych markerów raw client data/secrets;
  - Dreaming Mode jest opisany jako advisory-only i no-scheduler V1.
- Podłączyć validator do:
  - `validate-workflow`;
  - `check-required-artifacts`;
  - `check-validator-smoke-tests`;
  - `commands.md`, README i AGENTS validator list.
- Smoke tests:
  - brak policy failuje;
  - brak jednego z wariantów failuje;
  - brak `Dream variant` w template failuje;
  - brak privacy check w report template failuje;
  - raport z `.env`, API key, private key, email albo client name marker failuje;
  - wording typu “Dreaming Mode writes System Insights automatically” failuje;
  - brak no-scheduler V1 wording failuje;
  - poprawny anonymized `workflow-artifacts-only` report przechodzi bez repo/code review findings;
  - poprawny anonymized `full-repo` report przechodzi z repo/code review findings;
  - `update-workspace` tworzy brakujący `dreams/` namespace bez nadpisywania lokalnego raportu.

## Validation Plan

Po implementacji uruchomić:

```sh
git diff --check
.systems/scripts/check-dreaming-mode
.systems/scripts/check-validator-smoke-tests
.systems/scripts/validate-workflow
.systems/scripts/check-naming
.systems/scripts/check-required-artifacts
.systems/scripts/check-status-consistency
.systems/scripts/check-qa-evidence
.systems/scripts/check-system-insights
.systems/scripts/check-system-skills
.systems/scripts/check-contract-compliance
.systems/scripts/check-knowledge-capture-gate
.systems/scripts/check-default-quality-phase-chaining
git ls-files ai-workflow-workspace
```

## Assumptions

- Domyślny wariant to `workflow-artifacts-only`, bo jest bezpieczniejszy i tańszy.
- `full-repo` wymaga jawnej intencji ownera, bo czyta także target repo source.
- V1 nie dodaje schedulera, daemonów, hooków, cronów, automations ani background execution.
- Dream reports są workspace-owned advisory artifacts, nie phase artifacts i nie memory entries.
- Promocja z Dream Report do External Memory, System Insights, Project/Repo Memory albo skills wymaga późniejszej jawnej decyzji ownera i właściwego workflow.
- Dreaming Mode nie zmienia source-of-truth order, phase gates, risk, permissions, evidence, writes allowed, stop conditions ani owner approvals.
