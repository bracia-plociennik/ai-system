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

# Optional complete six-block food schedule. Keep each status explicit:
# configured requires all four numeric values; empty requires all four values blank.
training_block_09_11_status:
training_block_09_11_protein_g:
training_block_09_11_fat_g:
training_block_09_11_carbohydrates_g:
training_block_09_11_calorie_target:
training_block_11_13_status:
training_block_11_13_protein_g:
training_block_11_13_fat_g:
training_block_11_13_carbohydrates_g:
training_block_11_13_calorie_target:
training_block_13_15_status:
training_block_13_15_protein_g:
training_block_13_15_fat_g:
training_block_13_15_carbohydrates_g:
training_block_13_15_calorie_target:
training_block_15_17_status:
training_block_15_17_protein_g:
training_block_15_17_fat_g:
training_block_15_17_carbohydrates_g:
training_block_15_17_calorie_target:
training_block_17_19_status:
training_block_17_19_protein_g:
training_block_17_19_fat_g:
training_block_17_19_carbohydrates_g:
training_block_17_19_calorie_target:
training_block_19_21_status:
training_block_19_21_protein_g:
training_block_19_21_fat_g:
training_block_19_21_carbohydrates_g:
training_block_19_21_calorie_target:

rest_block_09_11_status:
rest_block_09_11_protein_g:
rest_block_09_11_fat_g:
rest_block_09_11_carbohydrates_g:
rest_block_09_11_calorie_target:
rest_block_11_13_status:
rest_block_11_13_protein_g:
rest_block_11_13_fat_g:
rest_block_11_13_carbohydrates_g:
rest_block_11_13_calorie_target:
rest_block_13_15_status:
rest_block_13_15_protein_g:
rest_block_13_15_fat_g:
rest_block_13_15_carbohydrates_g:
rest_block_13_15_calorie_target:
rest_block_15_17_status:
rest_block_15_17_protein_g:
rest_block_15_17_fat_g:
rest_block_15_17_carbohydrates_g:
rest_block_15_17_calorie_target:
rest_block_17_19_status:
rest_block_17_19_protein_g:
rest_block_17_19_fat_g:
rest_block_17_19_carbohydrates_g:
rest_block_17_19_calorie_target:
rest_block_19_21_status:
rest_block_19_21_protein_g:
rest_block_19_21_fat_g:
rest_block_19_21_carbohydrates_g:
rest_block_19_21_calorie_target:
---
```

Store an owner-approved populated copy only at `personal-ops/check-ins/check-in-settings.local.md`. It supplies timezone, the default V3 index policy, and owner-local budget reporting parameters. It contains no credentials. Budget values are private workspace data and are never populated automatically by init.

`private_index_policy_default` accepts `detailed-private` or `redacted`. Each canonical V3 report records its effective `private_index_policy`; a later settings change does not rewrite historical index policy.

`monthly_base_budget`, `monthly_buffer`, `daily_spending_pace`, `weekly_calorie_budget`, `training_day_standard`, and `rest_day_standard` are required by the budget calculator. `minimum_daily_calories` is optional; leave it blank until the owner explicitly configures it. A blank minimum produces no common-sense recommendation and never causes AI System to invent one.

The optional food schedule uses six fixed blocks: `09_11`, `11_13`, `13_15`, `15_17`, `17_19`, and `19_21`. A complete schedule must define every block for both `training` and `rest`. Use `empty` when no food is planned for a block. These values are read-only owner output and are never populated by init or copied into system-owned files.

After a check-in write, the populated configuration is consumed only after the official V3 `--post-write` refresh succeeds.
