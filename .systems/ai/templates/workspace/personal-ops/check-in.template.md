---
type: daily-check-in
schema_version: 3
date: <YYYY-MM-DD>
session_date: <YYYY-MM-DD>
previous_day_date: <YYYY-MM-DD>
timezone: <IANA timezone from check-in-settings.local.md>
source_type: manual-interpreted
normalization_authority: interpreted-report
report_revision: 1
task_generation_status: pending
task_generation_reason:
task_generation_references:
private_index_policy: detailed-private
plan_readiness: needs-prioritization
overload_status: none
overload_reasons:
overload_acknowledged: false
wig_plan_item_id:
wig_definition_of_done:
must_do_plan_item_ids:
task_candidate_eligible_count: 0
privacy: private-sensitive
---

# Daily Check-In <YYYY-MM-DD>

Normalized time fields accept `<HH:MM>`, `<YYYY-MM-DD HH:MM>`, or an ISO datetime. `HH:MM` is resolved from the section context: plan = `session_date`, closure = `previous_day_date`, sleep = `previous_day_date` to `session_date`.

## Metadane

- Data: <YYYY-MM-DD>
- Dzień tygodnia: <monday|tuesday|wednesday|thursday|friday|saturday|sunday>
- Godzina nagrania: <HH:MM>
- Konflikt daty i dnia tygodnia: <true|false>
- Źródło: <manual|voice-check-in|other>
- Prywatność: private-sensitive

## Podsumowanie poprzedniego dnia

### Sen

- Początek snu:
- Koniec snu:
- Jakość snu:
- Liczba przebudzeń:
- Przybliżenie snu:
- Sen raw:

### Faktyczny trening

- Faktyczny trening wykonany: <true|false|unknown>
- Faktyczny trening start:
- Faktyczny trening koniec:
- Faktyczny trening typ:
- RPE:
- Trening raw:

### Faktyczny NSDR

- Faktyczny NSDR wykonany: <true|false|unknown>
- Faktyczny NSDR start:
- Faktyczny NSDR koniec:
- Efekt NSDR:
- NSDR raw:

### Faktyczny IF i kalorie

- Faktyczny IF start:
- Faktyczny IF koniec:
- Faktyczne kalorie minimum:
- Faktyczne kalorie maksimum:
- Faktyczne kalorie reprezentatywne:
- IF raw:

### Finanse

- Finanse kwota:
- Finanse waluta:
- Finanse przybliżenie:
- Finanse raw:

### Faktycznie zbudowałem

- [actual-build-01] <actual item title>

### Faktycznie dowiozłem

- [actual-deliver-01] <actual item title>

### Faktycznie wypromowałem

- [actual-promote-01] <actual item title>

### Faktycznie zrobiłem coś dla siebie

- [actual-self-01] <actual item title>

### Faktycznie zrobiłem coś dla bliskich

- [actual-close-01] <actual item title>

### Faktyczne nawyki

- Habit ID: <habit-01>
  - Status: <completed|partial|not-completed|unknown>
  - Note:

### Porównanie plan-fakt

- plan_item_id:
  - status: <completed-as-planned|partial|not-completed|completed-differently|replaced|consciously-replanned|unknown|not-applicable>
  - actual_item_ids:
  - owner-approved: <true|false; required for completed-differently>
  - note:

### Minimum i refleksja

- Minimum dnia wyprowadzone: <completed|not-completed|unknown|not-defined; derived only from WIG comparison>
- Minimum dnia owner note: <optional explanation; does not override the derived value>
- Co realnie dało +1%:
- Co było zbędne:
- Zagrożenie dnia wystąpiło:
- Czy odpowiednio zareagowałem:

## Plan dnia

- Tryb pracy: <wzrost|obrona-reputacji|normalny|nie-podano>
- Tryb organizmu: <pelna-moc|normalny|regeneracja|nie-podano>

### Planowany trening

- Planowany trening start:
- Planowany trening koniec:
- Planowany trening typ:
- Trening raw:

### Planowany NSDR

- Planowany NSDR start:
- Planowany NSDR koniec:
- NSDR raw:

### Planowany IF i kalorie

- Planowany IF start:
- Planowany IF koniec:
- Planowane kalorie minimum:
- Planowane kalorie maksimum:
- Planowane kalorie reprezentatywne:
- IF raw:

### Budżet

- Budżet maksimum:
- Budżet waluta:
- Budżet raw:

### Planuję zbudować

- [build-01] <planned item title>
  - Task: <create|skip>
  - Task title: <optional TaskNote title>
  - Task bucket: <6d/do|6d/defer|6d/delegate|6d/delete|6d/dump>

### Planuję dowieźć

- [deliver-01] <planned item title>
  - Task: <create|skip>
  - Task title: <optional TaskNote title>
  - Task bucket: <6d/do|6d/defer|6d/delegate|6d/delete|6d/dump>

### Planuję wypromować

- [promote-01] <planned item title>
  - Task: <create|skip>
  - Task title: <optional TaskNote title>
  - Task bucket: <6d/do|6d/defer|6d/delegate|6d/delete|6d/dump>

### Planuję zrobić coś dla siebie

- [self-01] <planned item title>

### Planuję zrobić coś dla bliskich

- [close-01] <planned item title>

### Priorytety dnia

- WIG plan_item_id: <existing plan item ID>
- WIG definition of done: <observable completion condition>
- Must-do plan_item_ids: <comma-separated existing plan item IDs; maximum two; do not repeat WIG>
- Overload acknowledged: <true|false; owner-approved acknowledgement only>
- Priority owner note:

Items not named by WIG or Must-do are optional. WIG may be from any plan stream. Only professional WIG or must-do items from build, deliver, and promote are eligible for default TaskNotes.

### Planowane nawyki

- Habit ID: <habit-01>
  - Nazwa:
  - Trigger:
  - Kryterium:
  - Status: planned

## Poranny check-in

### Rutyna

- Pobudka bez negocjacji:
- Toaleta + mantra:
- Kuchnia:
- Dwór:
- Deep Focus:
- Życzenia dla bliskich:

### Aktualny stan

- Klarowność mentalna:
- Gotowość ciała:
- Ograniczenia:
- Wdzięczność:

## Dodatkowe informacje

- Uwagi:
- Uwagi interpretacyjne:
- Owner-authored reflection:
- Cytat/źródło:
  - source_status: <verified|unverified>

## Załączniki

- Relative asset path:
- Kind: <screenshot|note_image|ocr|other>

## Kandydaci na taski

Task candidates are derived only from planned `build-*`, `deliver-*`, and `promote-*` items. `Task: create` is the default when omitted; use `Task: skip` to opt out. `Task title` overrides the generated title. A single owner-approved V3 check-in write may create the corresponding TaskNotes if the local vault preflight passes. Do not create candidates from actual closure items.

## Opcjonalna interpretacja

Interpretation is advisory-only. It is not memory, System Insights, External Memory, or a verified source.

## Interpreted Input

This private-sensitive normalization record is appended by AI System after the canonical sections. Canonical V3 fields above are the source of truth for indexes and TaskNotes.

- Source type:
- Normalized values applied:
- Field mapping:
- Corrections applied: <later explicit owner correction wins for the named field>
- Unresolved fields:
- Precedence: canonical fields above take precedence over this audit context.
