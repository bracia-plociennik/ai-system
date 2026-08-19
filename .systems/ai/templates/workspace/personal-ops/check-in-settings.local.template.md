# Local Check-In Settings

This is a copyable local-only configuration shape. Do not create a populated configuration automatically and do not commit a private workspace configuration.

```yaml
---
timezone: Europe/Warsaw
private_index_policy_default: detailed-private
monthly_base_budget:
monthly_buffer:
daily_spending_pace:
monthly_budget_currency: PLN
weekly_calorie_budget:
training_day_standard:
rest_day_standard:
minimum_daily_calories:

# The calorie target comes from the saved check-in. The food profile is selected
# from the planned training/rest mode, never from the calorie target itself.
macro_target_protein_g: 180
macro_target_fat_g: 80
macro_calorie_tolerance_kcal: 90

# Each profile defines six fixed blocks. Configured values are macro shares;
# carbohydrates are calculated as the residual after protein and fat.
macro_training_block_09_11_status: empty
macro_training_block_11_13_status: configured
macro_training_block_11_13_protein_share_percent: 33
macro_training_block_11_13_fat_share_percent: 25
macro_training_block_11_13_carbohydrates_share_percent: 42
macro_training_block_13_15_status: empty
macro_training_block_15_17_status: configured
macro_training_block_15_17_protein_share_percent: 31
macro_training_block_15_17_fat_share_percent: 19
macro_training_block_15_17_carbohydrates_share_percent: 23
macro_training_block_17_19_status: empty
macro_training_block_19_21_status: configured
macro_training_block_19_21_protein_share_percent: 36
macro_training_block_19_21_fat_share_percent: 56
macro_training_block_19_21_carbohydrates_share_percent: 36

macro_rest_block_09_11_status: empty
macro_rest_block_11_13_status: configured
macro_rest_block_11_13_protein_share_percent: 33
macro_rest_block_11_13_fat_share_percent: 38
macro_rest_block_11_13_carbohydrates_share_percent: 36
macro_rest_block_13_15_status: empty
macro_rest_block_15_17_status: configured
macro_rest_block_15_17_protein_share_percent: 31
macro_rest_block_15_17_fat_share_percent: 19
macro_rest_block_15_17_carbohydrates_share_percent: 18
macro_rest_block_17_19_status: empty
macro_rest_block_19_21_status: configured
macro_rest_block_19_21_protein_share_percent: 36
macro_rest_block_19_21_fat_share_percent: 44
macro_rest_block_19_21_carbohydrates_share_percent: 46

# Chronological Daily V4 schedule. Each planned professional item may reference
# one of these block_id values; missing block_id remains explicitly unallocated.
# Keep this fallback generic: no client names, dated tasks, or dated deadlines.
schedule_historical_overrides_json: {}
schedule_standard_json: [{"block_id":"routine","start":"07:30","end":"09:00","label":"Rutyna poranna","dod":"Rutyna wykonana","deadline":"—"},{"block_id":"build-future","start":"09:10","end":"10:40","label":"Build","dod":"Blok build zakończony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-1","start":"10:40","end":"10:50","label":"Checkpoint OSNR","dod":"O/S/N/R zapisane","deadline":"—"},{"block_id":"meal-1","start":"11:00","end":"11:30","label":"Śniadanie","dod":"Posiłek zgodny z harmonogramem makro","deadline":"—"},{"block_id":"adapt-build-deliver","start":"11:40","end":"12:40","label":"Adaptacja","dod":"Zakres adaptacji zakończony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-2","start":"12:40","end":"12:50","label":"Checkpoint OSNR","dod":"O/S/N/R zapisane","deadline":"—"},{"block_id":"training","start":"13:10","end":"15:10","label":"Trening","dod":"Trening wykonany albo jawnie odroczony","deadline":"—"},{"block_id":"nsdr","start":"15:50","end":"16:20","label":"NSDR","dod":"Sesja NSDR wykonana albo jawnie pominięta","deadline":"—"},{"block_id":"deliver-financial-impact","start":"16:30","end":"17:30","label":"Deliver","dod":"Najważniejszy rezultat dowieziony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-3","start":"17:30","end":"17:40","label":"Checkpoint OSNR","dod":"O/S/N/R zapisane","deadline":"—"},{"block_id":"adapt-promote-deliver","start":"17:50","end":"18:50","label":"Adaptacja / promocja / deliver","dod":"Zakres zakończony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-4","start":"18:50","end":"19:00","label":"Checkpoint OSNR","dod":"Dzień pracy zamknięty i Resume zapisane","deadline":"—"},{"block_id":"meal-2","start":"19:00","end":"21:00","label":"Obiado-kolacja","dod":"Posiłek zgodny z harmonogramem makro","deadline":"—"},{"block_id":"shutdown","start":"22:30","end":"23:00","label":"Shutdown","dod":"Ekrany wyłączone i dzień zamknięty","deadline":"—"}]
schedule_merged_adapt_shifted_json: [{"block_id":"routine","start":"07:30","end":"09:00","label":"Rutyna poranna","dod":"Rutyna wykonana","deadline":"—"},{"block_id":"build-future","start":"09:10","end":"10:40","label":"Build","dod":"Blok build zakończony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-1","start":"10:40","end":"10:50","label":"Checkpoint OSNR","dod":"O/S/N/R zapisane","deadline":"—"},{"block_id":"meal-1","start":"11:00","end":"11:30","label":"Śniadanie","dod":"Posiłek zgodny z harmonogramem makro","deadline":"—"},{"block_id":"adapt-merged","start":"11:40","end":"13:40","label":"Adaptacja scalona","dod":"Zakres adaptacji zakończony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-2","start":"13:40","end":"13:50","label":"Checkpoint OSNR","dod":"O/S/N/R zapisane","deadline":"—"},{"block_id":"training-shifted","start":"14:10","end":"16:10","label":"Trening przesunięty","dod":"Trening wykonany albo jawnie odroczony","deadline":"—"},{"block_id":"nsdr-shifted","start":"16:50","end":"17:20","label":"NSDR przesunięty","dod":"Sesja NSDR wykonana albo jawnie pominięta","deadline":"—"},{"block_id":"deliver-shifted","start":"17:30","end":"18:30","label":"Deliver przesunięty","dod":"Najważniejszy rezultat dowieziony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-3","start":"18:30","end":"18:40","label":"Checkpoint OSNR","dod":"O/S/N/R zapisane","deadline":"—"},{"block_id":"adapt-promote-deliver-shifted","start":"18:50","end":"19:50","label":"Adaptacja przesunięta","dod":"Zakres zakończony lub ma zapisany OSNR","deadline":"—"},{"block_id":"osnr-4","start":"19:50","end":"20:00","label":"Checkpoint OSNR","dod":"Dzień pracy zamknięty i Resume zapisane","deadline":"—"},{"block_id":"meal-2-shifted","start":"20:00","end":"22:00","label":"Obiado-kolacja przesunięta","dod":"Posiłek zgodny z harmonogramem makro","deadline":"—"},{"block_id":"shutdown-shifted","start":"23:30","end":"00:00","label":"Shutdown przesunięty","dod":"Ekrany wyłączone i dzień zamknięty","deadline":"—"}]
---
```

Store an owner-approved populated copy only at `personal-ops/check-ins/check-in-settings.local.md`. It supplies timezone, the default V3 index policy, owner-local budget reporting parameters, and private calorie-target profiles. It contains no credentials. Budget and macro values are private workspace data and are never populated automatically by init.

`private_index_policy_default` accepts `detailed-private` or `redacted`. Each canonical V3 report records its effective `private_index_policy`; a later settings change does not rewrite historical index policy.

The daily food schedule is selected by the check-in's planned training/rest mode. The independent `planned_calories_representative` value sets the total calorie target. Protein and fat are anchored by the shared targets while carbohydrates are calculated as the residual.

`monthly_base_budget`, `monthly_buffer`, `daily_spending_pace`, `weekly_calorie_budget`, `training_day_standard`, and `rest_day_standard` are required by the budget calculator. `minimum_daily_calories` is optional; leave it blank until the owner explicitly configures it. A blank minimum produces no common-sense recommendation and never causes AI System to invent one.

Food profiles use `macro_training` and `macro_rest`; planned training with a complete type and time selects `training`, explicit no-training selects `rest`, and missing or ambiguous training data remains `unknown`. A complete profile defines six fixed blocks: `09_11`, `11_13`, `13_15`, `15_17`, `17_19`, and `19_21`. Use `empty` when no food is planned for a block. Profiles are read-only owner output and are never populated by init or copied into system-owned files.

New Daily V4 artifacts use `daily_plan_contract: per-day-schedule-v1` and carry their own `planned_schedule_json`. `schedule_historical_overrides_json` is only a date-keyed compatibility map for already-saved V4 artifacts. Generic schedule variants remain the final legacy fallback and must never contain customer-specific or dated work.

After a check-in write, the populated configuration is consumed only after the official V3 `--post-write` refresh succeeds.
