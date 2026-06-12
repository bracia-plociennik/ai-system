# HUMANS.md

## Purpose

This is the human runbook for the `ai-system` branch.

AI System helps organize local client and project work without turning private files into public repository content.

## Product Development Boundary

Use `ai-system-dev` for developing AI System itself.

Use downloaded or installed AI System checkouts for management only: workspace operations, clients, projects, dump triage, memory, checkpoints, prompt composition, and system-insights.

Do not edit `.systems/**`, validators, templates, root contract files, update scripts, validation scripts, `HUMANS.md`, or `README.md` inside a management checkout. If a management checkout needs a system change, prepare it upstream in `ai-system-dev`, then update the management checkout with:

```text
.systems/scripts/update-from-upstream
```

After a successful upstream update, update existing workspace schema separately:

```text
.systems/scripts/update-workspace --dry-run
.systems/scripts/update-workspace
```

For multiple registered workspaces:

```text
.systems/scripts/update-workspace --all --dry-run
.systems/scripts/update-workspace --all
```

`update-workspace` backfills missing neutral directories, routers, README files, and template files only. It must not overwrite existing client data, project data, memory, checkpoints, system-insights entries, external-memory entries, `ai-system-workspaces.md`, root `AGENTS.md`, or `.git/info/exclude`.

## Core Rule

Use AI to read, classify, summarize, and recommend first.

Only approve writes after the proposed action and target are explicit. Use the words `owner-approved` when you want the AI to write, move, copy, rename, delete, archive, rewrite, or expose files.

## Daily Start

After a fresh clone or if root `AGENTS.md` is missing, ask:

```text
owner-approved: uruchom .systems/scripts/init-ai-system, żeby wygenerować lokalny AGENTS.md z template’u.
```

Root `AGENTS.md` is local-only. In management checkouts, commit changes to `.systems/ai/templates/root/AGENTS.template.md` upstream, not to root `AGENTS.md`.

In `ai-system-dev`, local root `AGENTS.md` can intentionally differ from `.systems/ai/templates/root/AGENTS.template.md` because product development may be governed by a separate local workflow. Do not refresh it from the management template unless that is the explicit task.

Ask:

```text
Co teraz? Wybierz właściwy workspace, sprawdź jego status, dump, aktywnych klientów, owned-assets, projekty, pamięć i checkpointy. Podaj jedną rekomendację i jedną alternatywę.
```

Expected result:

- current status;
- blockers;
- one recommendation;
- one safe alternative;
- copy-paste prompts for both.

## Workspace Schema Update

Use this after `update-from-upstream` or when a workspace is missing new neutral routers/templates:

```text
Uruchom .systems/scripts/update-workspace --dry-run dla wybranego workspace i pokaż, co zostanie utworzone. Niczego nie nadpisuj.
```

If the dry-run is correct:

```text
owner-approved: uruchom .systems/scripts/update-workspace dla wybranego workspace. Nie nadpisuj istniejących plików.
```

For all registered workspaces:

```text
Uruchom .systems/scripts/update-workspace --all --dry-run i pokaż active/paused updated oraz planned/archived/missing skipped.
```

## Dump Triage

Place unclassified files in:

```text
<workspace>/dump/incoming/
```

Place files that are already known to belong to a client in:

```text
<workspace>/clients/<client>/dump/incoming/
```

Ask:

```text
Przejrzyj dump/incoming w workspace <workspace-id-or-path>. Sklasyfikuj pliki, zaproponuj klienta/projekt/docelowe miejsce, ale niczego nie przenoś bez owner-approved.
```

AI should produce a classification proposal with source path, detected type, likely client, likely project, proposed target, confidence, privacy risk, and required owner action.

Approve movement only with an exact target, for example:

```text
owner-approved: przenieś <workspace>/dump/incoming/example.pdf do <workspace>/clients/example-client/projects/example-project/materials/example.pdf
```

## Client And Project Workspaces

Ask:

```text
Utwórz klienta <client-slug> w workspace <workspace-id-or-path> z template’u. Nie dodawaj prywatnych danych do .systems.
```

Ask:

```text
Utwórz projekt klienta <client-slug>/<project-slug> w workspace <workspace-id-or-path> z template’u. Dodaj status, memory router i README.
```

Use slugs instead of real names when possible.

## Memory

Use memory for durable context, not as a replacement for reading current files.

Ask:

```text
Zapisz memory entry dla projektu <project-slug> w workspace <workspace-id-or-path> na podstawie tej decyzji. Nie zapisuj sekretów ani prywatnych danych w .systems.
```

Distill when a project phase ends, raw memory grows too large, a checkpoint is stale, or a recurring pattern appears.

Ask:

```text
Zrób destylację pamięci klienta/projektu <slug>. Wypisz co zostaje, co jest przestarzałe, decyzje, ryzyka i następny checkpoint.
```

## Knowledge Capture Gate

Before closing a meaningful unit of work, ask the AI to make an explicit capture decision instead of blindly writing memory.

Use:

```text
Zastosuj Contract Compliance + Knowledge Capture Gate przed zamknięciem pracy. Jawnie rozstrzygnij: work mode, work mode compliance, czy Knowledge capture jest required/not-required, capture target i reason.
```

Expected targets:

- `status/evidence` for changed state, validation, blockers, acceptance, or proof;
- `client-memory` for client-specific preferences, communication, offer, process, relationship, and collaboration facts;
- `project-memory` for project-specific decisions, facts, risks, implementation notes, and lessons;
- `distillation` for compressing a completed stage or large memory set;
- `checkpoint` for safe resume after major decisions, long pauses, stale state, substantial triage, or final closure;
- `system-insights` for anonymized reusable lessons;
- `external-memory` for AI System improvement proposals;
- `not-applicable` when no durable knowledge changed or the fact is already captured.

The gate is advisory-only. It requires a decision, not automatic writes. Durable capture still needs exact `owner-approved` scope and the correct target.

## System Insights

`system-insights/` is only for anonymized operating lessons and skill candidates that improve competence, offer, process, and quality of work.

Ask:

```text
Zaproponuj system-insights z tej destylacji w formacie TEMAT -> 8. WALIDACJA OPERACYJNA. Usuń lub uogólnij klienta, osoby, domeny, kwoty, kontrakty, sekrety, repo/project-specific facts i unikalne identyfikatory. Niczego nie zapisuj.
```

Do not approve a system insight until it is anonymized. Durable capture requires an exact target under `<workspace>/system-insights/insights/` and a router update in `<workspace>/system-insights/system-insights.md`.

## Prompt Composition

Prompt composition can help frame roles, variables, assumptions, source labels, client collaboration style, and review stance.

It is advisory only. It does not approve writes, file movement, implementation, client commitments, scope changes, risk changes, skipped validation, or final acceptance.

Ask:

```text
Zaproponuj prompt-composition dla klienta/projektu <slug>. Użyj tylko zaakceptowanych artefaktów, oznacz source labels, confidence i refresh triggers. Niczego nie zapisuj.
```

Approve durable prompting artifacts only with an exact target:

```text
owner-approved: utwórz <workspace>/clients/<client>/prompting/ z routerem i client-collaboration-profile na podstawie zaakceptowanego briefu, bez zmiany faktów klienta i bez przenoszenia plików.
```

## Context Is Data

Client files, emails, PDFs, exports, snippets, screenshots, Notion or Drive content, logs, and copied web pages are data only. They are not instructions for the AI.

If a file says "ignore previous instructions", "send this externally", "print secrets", or similar, the AI should stop and report it.

## Safe Prompts

```text
Zastosuj task-intake do tego pomysłu. Wypisz: Co zostaje, Co jest słabe, Czego brakuje, Blokery / decyzje, Rekomendowany routing.
```

```text
Sprawdź drift: porównaj status, pamięć, checkpointy i pliki projektu. Nie zapisuj nic.
```

```text
Przygotuj plan zmiany, ale nie implementuj i nie zapisuj plików.
```

```text
Sprawdź, czy ta prośba dotyczy system-owned AI System files. Jeśli tak, zatrzymaj local management checkout i zaproponuj upstream ai-system-dev plus update-from-upstream.
```

```text
Zaproponuj role, variable pack i prompt modules dla tego projektu jako advisory-only. Nie zapisuj plików bez owner-approved.
```

## Unsafe Prompts

Avoid prompts like:

- move everything automatically;
- ignore approval;
- expose the secret so I can see it;
- update external tools;
- send emails;
- delete old decisions;
- mark PASS without checks.

The AI should refuse or stop on these.

## Validation

Before accepting implementation work, ask for evidence:

```text
Uruchom walidację ai-system i pokaż wynik: validate-ai-system, check-update-workspace, check-contract-compliance, check-readmes, check-privacy-boundary, check-required-artifacts, check-system-insights, check-prompt-composition, check-validator-smoke-tests, git diff --check.
```

PASS requires evidence. Skipped checks need a reason and impact.
