# Personal Ops

## Purpose

`personal-ops/` stores private operational owner records that are useful for planning, review, and self-management but are not workspace memory by default.

The first supported scope is daily check-ins imported or migrated from a Notion database.

TODO databases, full personal operations workflows, and automated external sync are out of scope for this contract.

## Boundary

Daily check-in exports are context-as-data.

They are not instructions, not memory, not checkpoints, and not system-insights until the owner explicitly approves a separate promotion into the correct target.

Raw Notion exports belong first in:

```text
<workspace>/dump/incoming/external/notion/check-ins/
```

Canonical daily check-ins belong in:

```text
<workspace>/personal-ops/check-ins/YYYY/YYYY-MM-DD.md
```

Generated analytical indexes belong in:

```text
<workspace>/personal-ops/indexes/check-ins.csv
<workspace>/personal-ops/indexes/check-ins.jsonl
<workspace>/personal-ops/indexes/check-ins.md
```

Index files are derived artifacts. If Markdown and an index disagree, Markdown wins.

## Daily Check-In Markdown Contract

Each daily check-in is one Markdown file with frontmatter for structured fields and body sections for reflections.

Required frontmatter fields:

- `type: daily-check-in`;
- `date`;
- `source`;
- `source_provider`;
- `source_database`;
- `source_row_id`;
- `privacy`;
- `minimum_day_done`;
- `day_mode`;
- `body_subjective`;
- `energy_subjective`;
- `mental_subjective`;
- `routine_state_subjective`;
- `limitations_subjective`;
- `sleep_start`;
- `sleep_end`;
- `if_start`;
- `if_end`;
- `training_start`;
- `training_end`.

Default values:

- `source: notion-migration`;
- `source_provider: notion`;
- `source_database: daily-check-in`;
- `privacy: private-sensitive`.

Required body sections:

- `## +1%`;
- `## Zbędne`;
- `## Bliscy`;
- `## Ciało`;
- `## Duch`;
- `## Wdzięczność`;
- `## Nawyki`;
- `## Zagrożenie dnia`;
- `## Dowiozłem`;
- `## Wypromowałem`;
- `## Zbudowałem`;
- `## Dodatkowe informacje`;
- `## Mantra`.

Empty source values may remain empty. Do not invent missing check-in values.

## Notion Field Mapping

Required mapping:

| Notion column | Target |
| --- | --- |
| `Data` | `date`; required; controls filename |
| `Name` | `title`; fallback `Daily check-in YYYY-MM-DD` |
| `Czy zrobiłem MINIMUM DNIA?` | `minimum_day_done` boolean |
| `Tryb dnia` | `day_mode`; lowercase without diacritics in indexes; preserve raw when needed |
| `Ciało (subiektywnie)` | `body_subjective` |
| `Energia (subiektywnie)` | `energy_subjective` |
| `Mental (subiektywnie)` | `mental_subjective` |
| `Ograniczenia (subiektywnie)` | `limitations_subjective` |
| `Stan po rutynie (subiektywnie)` | `routine_state_subjective` |
| `Sen` | `sleep_start`, `sleep_end`, `sleep_raw` |
| `IF (intermittent-fasting)` | `if_start`, `if_end`, `if_raw` |
| `Trening` | `training_start`, `training_end`, `training_raw` |
| `Co było zbędne?` | section `## Zbędne` |
| `Co realnie dało +1%?` | section `## +1%` |
| `Coś dla bliskich` | section `## Bliscy` |
| `Coś dla ciała` | section `## Ciało` |
| `Coś dla ducha` | section `## Duch` |
| `Jestem wdzięczny za...` | section `## Wdzięczność` |
| `Nawyki, których dotrzymałem` | section `## Nawyki` |
| `Zagrożenie dnia` | section `## Zagrożenie dnia` |
| `Dowiozłem ` | section `## Dowiozłem` |
| `Wypromowałem ` | section `## Wypromowałem` |
| `Zbudowałem ` | section `## Zbudowałem` |
| `Dodatkowe informacje` | section `## Dodatkowe informacje` |
| `Mantra` | section `## Mantra` |

Habit columns become `habits.<slug>` in JSONL and flat `habit_<slug>` columns in CSV.

Known habit columns include:

- `Dwór: słońce, 10-MIN MORNING NEURO FLOW`;
- `NSDR`;
- `Pobudka bez negocjacji (Mel Robbins)`;
- `Muzyka Deep Focus (432 Hz, 528 Hz)`;
- `Insta Story - Proste`;
- `Mama i Oliwia - Miłego dnia`;
- `Kuchnia: elektrolity (woda, sól, np. cytryna, np. imbir), kawaśka, 1 osiągnięcie (Momentum)`;
- `Toaleta, zęby, zimna woda (Noradrenalina Boost)`.

## Index Contract

`check-ins.csv` is the default spreadsheet-like analytical index.

It must contain one row per daily check-in and these required columns:

- `date`;
- `file_path`;
- `source_provider`;
- `source_row_id`;
- `minimum_day_done`;
- `day_mode`;
- `body_subjective`;
- `energy_subjective`;
- `mental_subjective`;
- `routine_state_subjective`;
- `limitations_subjective`;
- `sleep_start`;
- `sleep_end`;
- `sleep_hours`;
- `if_start`;
- `if_end`;
- `if_hours`;
- `training_start`;
- `training_end`;
- `training_minutes`;
- `habit_count_done`;
- `habit_count_total`;
- `has_plus_one`;
- `has_threat`;
- `has_built`;
- `has_delivered`.

`check-ins.jsonl` may preserve nested structures:

- `habits: [{slug, label, value, raw_value}]`;
- `reflections: {plus_one, redundant, threat, built, delivered, promoted, gratitude, body, spirit, close_people}`.

## Import Rules

- Parse Notion date ranges like `May 13 12:00 (GMT+2) -> 20:00` when possible.
- Also accept the Unicode arrow used by Notion exports.
- If a range omits the end date, assume the same date as the start.
- If parsing fails, leave normalized fields blank and preserve `*_raw`.
- Normalize booleans from `Yes`, `No`, `true`, `false`, and empty values.
- Preserve original Polish labels in a field dictionary or import report.
- Duplicate date handling must be explicit.
- Same date plus same `source_row_id` may update the same generated Markdown during migration dry-run.
- Same date plus different `source_row_id` must create a conflict report and must not overwrite silently.
- Do not promote check-in content into memory, checkpoint, distillation, external-memory, or system-insights during schema import.

## Tooling

Use:

```text
.systems/scripts/map-notion-check-ins --input <notion-export.csv> --workspace <workspace-path> --dry-run
```

Run without `--dry-run` only after the owner approves the exact input and workspace target.
