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

# Define one complete six-block profile per exact planned calorie target.
# Protein and fat can stay approximately stable; carbohydrates can rotate.
# Each profile must define every block. Use empty with all numeric fields blank.
calorie_2300_block_09_11_status:
calorie_2300_block_09_11_protein_g:
calorie_2300_block_09_11_fat_g:
calorie_2300_block_09_11_carbohydrates_g:
calorie_2300_block_09_11_calorie_target:
calorie_2300_block_11_13_status:
calorie_2300_block_11_13_protein_g:
calorie_2300_block_11_13_fat_g:
calorie_2300_block_11_13_carbohydrates_g:
calorie_2300_block_11_13_calorie_target:
calorie_2300_block_13_15_status:
calorie_2300_block_13_15_protein_g:
calorie_2300_block_13_15_fat_g:
calorie_2300_block_13_15_carbohydrates_g:
calorie_2300_block_13_15_calorie_target:
calorie_2300_block_15_17_status:
calorie_2300_block_15_17_protein_g:
calorie_2300_block_15_17_fat_g:
calorie_2300_block_15_17_carbohydrates_g:
calorie_2300_block_15_17_calorie_target:
calorie_2300_block_17_19_status:
calorie_2300_block_17_19_protein_g:
calorie_2300_block_17_19_fat_g:
calorie_2300_block_17_19_carbohydrates_g:
calorie_2300_block_17_19_calorie_target:
calorie_2300_block_19_21_status:
calorie_2300_block_19_21_protein_g:
calorie_2300_block_19_21_fat_g:
calorie_2300_block_19_21_carbohydrates_g:
calorie_2300_block_19_21_calorie_target:

calorie_2500_block_09_11_status:
calorie_2500_block_09_11_protein_g:
calorie_2500_block_09_11_fat_g:
calorie_2500_block_09_11_carbohydrates_g:
calorie_2500_block_09_11_calorie_target:
calorie_2500_block_11_13_status:
calorie_2500_block_11_13_protein_g:
calorie_2500_block_11_13_fat_g:
calorie_2500_block_11_13_carbohydrates_g:
calorie_2500_block_11_13_calorie_target:
calorie_2500_block_13_15_status:
calorie_2500_block_13_15_protein_g:
calorie_2500_block_13_15_fat_g:
calorie_2500_block_13_15_carbohydrates_g:
calorie_2500_block_13_15_calorie_target:
calorie_2500_block_15_17_status:
calorie_2500_block_15_17_protein_g:
calorie_2500_block_15_17_fat_g:
calorie_2500_block_15_17_carbohydrates_g:
calorie_2500_block_15_17_calorie_target:
calorie_2500_block_17_19_status:
calorie_2500_block_17_19_protein_g:
calorie_2500_block_17_19_fat_g:
calorie_2500_block_17_19_carbohydrates_g:
calorie_2500_block_17_19_calorie_target:
calorie_2500_block_19_21_status:
calorie_2500_block_19_21_protein_g:
calorie_2500_block_19_21_fat_g:
calorie_2500_block_19_21_carbohydrates_g:
calorie_2500_block_19_21_calorie_target:
---
```

Store an owner-approved populated copy only at `personal-ops/check-ins/check-in-settings.local.md`. It supplies timezone, the default V3 index policy, owner-local budget reporting parameters, and private calorie-target profiles. It contains no credentials. Budget and macro values are private workspace data and are never populated automatically by init.

`private_index_policy_default` accepts `detailed-private` or `redacted`. Each canonical V3 report records its effective `private_index_policy`; a later settings change does not rewrite historical index policy.

The daily food schedule is selected by the check-in's `planned_calories_representative` value, not by training/rest mode. Keep protein and fat approximately stable while rotating carbohydrates between exact calorie-target profiles.

`monthly_base_budget`, `monthly_buffer`, `daily_spending_pace`, `weekly_calorie_budget`, `training_day_standard`, and `rest_day_standard` are required by the budget calculator. `minimum_daily_calories` is optional; leave it blank until the owner explicitly configures it. A blank minimum produces no common-sense recommendation and never causes AI System to invent one.

Food profiles use exact target names such as `calorie_2300` and `calorie_2500`; the daily check-in's `planned_calories_representative` selects the profile. Training/rest mode and planned training time never select macro blocks. A complete profile defines six fixed blocks: `09_11`, `11_13`, `13_15`, `15_17`, `17_19`, and `19_21`. Use `empty` when no food is planned for a block. Profiles are read-only owner output and are never populated by init or copied into system-owned files.

After a check-in write, the populated configuration is consumed only after the official V3 `--post-write` refresh succeeds.
