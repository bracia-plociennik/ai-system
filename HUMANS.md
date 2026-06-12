# HUMANS.md

## Purpose

This is the human runbook for the `ai-system` branch.

AI System helps organize local client and project work without turning private files into public repository content.

## Core Rule

Use AI to read, classify, summarize, and recommend first.

Only approve writes after the proposed action and target are explicit. Use the words `owner-approved` when you want the AI to write, move, copy, rename, delete, archive, rewrite, or expose files.

## Daily Start

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

## System Insights

`system-insights/` is only for anonymized lessons that improve competence, offer, process, and quality of work.

Ask:

```text
Zaproponuj system-insights z tej destylacji. Usuń lub uogólnij klienta, osoby, domeny, kwoty, kontrakty, sekrety i unikalne identyfikatory.
```

Do not approve a system insight until it is anonymized.

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
Uruchom walidację ai-system i pokaż wynik: validate-ai-system, check-readmes, check-privacy-boundary, check-required-artifacts, check-prompt-composition, check-validator-smoke-tests, git diff --check.
```

PASS requires evidence. Skipped checks need a reason and impact.
