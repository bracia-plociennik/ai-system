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
---
```

Store an owner-approved populated copy only at `personal-ops/check-ins/check-in-settings.local.md`. It supplies timezone, the default V3 index policy, owner-local budget reporting parameters, and private calorie-target profiles. It contains no credentials. Budget and macro values are private workspace data and are never populated automatically by init.

`private_index_policy_default` accepts `detailed-private` or `redacted`. Each canonical V3 report records its effective `private_index_policy`; a later settings change does not rewrite historical index policy.

The daily food schedule is selected by the check-in's planned training/rest mode. The independent `planned_calories_representative` value sets the total calorie target. Protein and fat are anchored by the shared targets while carbohydrates are calculated as the residual.

`monthly_base_budget`, `monthly_buffer`, `daily_spending_pace`, `weekly_calorie_budget`, `training_day_standard`, and `rest_day_standard` are required by the budget calculator. `minimum_daily_calories` is optional; leave it blank until the owner explicitly configures it. A blank minimum produces no common-sense recommendation and never causes AI System to invent one.

Food profiles use `macro_training` and `macro_rest`; planned training with a complete type and time selects `training`, explicit no-training selects `rest`, and missing or ambiguous training data remains `unknown`. A complete profile defines six fixed blocks: `09_11`, `11_13`, `13_15`, `15_17`, `17_19`, and `19_21`. Use `empty` when no food is planned for a block. Profiles are read-only owner output and are never populated by init or copied into system-owned files.

After a check-in write, the populated configuration is consumed only after the official V3 `--post-write` refresh succeeds.
