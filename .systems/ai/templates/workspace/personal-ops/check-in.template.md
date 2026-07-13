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
privacy: private-sensitive
---

# Daily Check-In <YYYY-MM-DD>

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

- Faktyczny trening start:
- Faktyczny trening koniec:
- Faktyczny trening typ:
- RPE:
- Trening raw:

### Faktyczny NSDR

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

### Faktyczne nawyki

- Habit ID: <habit-01>
  - Status: <completed|partial|not-completed|unknown>
  - Note:

### Porównanie plan-fakt

- plan_item_id:
  - status: <completed-as-planned|partial|not-completed|completed-differently|replaced|consciously-replanned|unknown|not-applicable>
  - actual_item_ids:
  - note:

### Minimum i refleksja

- Minimum dnia: <completed|partial|not-completed|not-defined|unknown>
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

### Planuję dowieźć

- [deliver-01] <planned item title>

### Planuję wypromować

- [promote-01] <planned item title>

### Planuję zrobić coś dla siebie

- [self-01] <planned item title>

### Planuję zrobić coś dla bliskich

- [close-01] <planned item title>

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
- Cytat/źródło: <unverified unless source is checked>

## Załączniki

- Relative asset path:
- Kind: <screenshot|note_image|ocr|other>

## Kandydaci na taski

Task candidates are derived only from planned `build-*`, `deliver-*`, and `promote-*` items. A single owner-approved V3 check-in write may create the corresponding TaskNotes if the local vault preflight passes. Do not create candidates from actual closure items.

## Opcjonalna interpretacja

Interpretation is advisory-only. It is not memory, System Insights, External Memory, or a verified source.
