# Personal Ops V3: luka fazy jakości

Date: 2026-07-13
Scope: AI System product implementation review
Status: process improvement candidate
Privacy: no client or personal runtime data

## Problem

Podczas implementacji Personal Ops Daily Check-In v3 uruchomiono walidatory i smoke testy, ale nie wykonano wystarczająco głębokiego review semantyki cross-day ani adversarialnych przypadków danych. Final review ujawnił błędy, które wcześniejsze testy przepuściły.

## Dlaczego nie zostały wykazane wcześniej

- Walidacja skupiała się na obecności kontraktu i happy-pathach, nie na invariants po merge sesji D oraz closure D+1.
- Brakowało fixtures dla: closure bez poprzedniego V3 planu, dynamicznych nawyków zamykanych następnego dnia oraz ochrony metadata effective-day.
- Review implementacji nie prześledził ręcznie danych od wejścia przez parser do scalonego CSV/JSONL.
- Test podobnych TaskNotes pokrywał tylko AI System `project`/`client`, nie standardowe TaskForge `projects:`.
- Kontrakt `task_generation_status: skipped` został opisany, lecz nie zweryfikowano, czy istnieje narzędzie zdolne atomowo zapisać ten status przy nieudanym preflight vaulta.

## Lekcje operacyjne

- Dla parserów cross-day wymagaj testów invariantów: metadane dnia efektywnego nie mogą zostać zastąpione metadanymi sesji closure.
- Każde pole planowane, które ma analitykę wykonania, musi mieć osobny model actual/closure; nie wolno zakładać edycji historycznego planu.
- Sentinel values (`unknown`, `not-defined`, `brak`) muszą mieć testy negatywne i nie mogą samodzielnie tworzyć faktów, closure ani metryk.
- Integracje z aplikacją Markdown muszą testować zarówno lokalny schema contract, jak i wspierane natywne pola aplikacji.
- Wymóg trwałego statusu po błędzie musi mieć właściciela wykonania: mechanizm zapisu albo jawne ograniczenie kontraktu. Sama dokumentacja nie stanowi dowodu egzekwowalności.

## Zmiana procesu

Przed final review zmian modelu danych należy przygotować matrix: source shape, expected canonical state, expected derived rows, forbidden rows, oraz failure behavior. Smoke tests muszą obejmować każdy wiersz matrixu, a review powinien ręcznie sprawdzić co najmniej jeden cross-day merge i jeden failure path.

## Routing

Ta notatka dotyczy usprawnienia procesu AI Workflow. Nie zmienia kontraktu AI System i nie zatwierdza implementacji V3.
