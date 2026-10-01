# Personal Ops Budget Reporting

## Purpose

This contract defines owner-local reporting for spending and calorie budgets. It is an advisory calculation layer over official indexes; it does not change canonical source schemas and does not provide medical, dietary, tax, or financial advice.

The calculator reads the local configuration and the official version-aware read model:

- `<workspace>/personal-ops/check-ins/check-in-settings.local.md`;
- unified workspace: the complete hashed generation selected by `<workspace>/personal-ops/indexes/check-ins-v4-active`, with its V4 JSONL, manifest and source inventory;
- unmigrated workspace: compatible V3/V4 canonical properties and `<workspace>/personal-ops/indexes/check-ins-v3.jsonl` / `check-ins-v3.md` freshness metadata, preserving existing behavior.

It must stop when the local configuration is missing, malformed, or when official indexes are missing or stale. It must never fall back to hard-coded owner values.

## Unified Aggregate Coverage

After aggregate activation, `.systems/ai/core/personal-ops-aggregates-v4.md` governs dated observations and coverage instead of the legacy scalar-only arithmetic below. Records remain as-of the report date; facts before that date are selected by explicit closure/review periods. Equal repeated facts deduplicate; conflicting values or partial overlaps stop arithmetic. Multi-day amounts remain undivided. Unknown legacy defaults are not observed zero; incomplete periods show known subtotals and missing dates, with full balances and derived limits unknown. Weekly canonical facts are not added again. An empty elapsed period at a month/week boundary can be complete with zero; that does not assert today's consumption or spending is zero.

## Local Configuration

The owner may create a populated copy of the local settings template at:

```text
<workspace>/personal-ops/check-ins/check-in-settings.local.md
```

The configuration contains no credentials and is `private-sensitive` workspace data. Required values are:

```yaml
monthly_base_budget: <number>
monthly_buffer: <number>
daily_spending_pace: <number>
monthly_budget_currency: PLN
weekly_calorie_budget: <number>
training_day_standard: <number>
rest_day_standard: <number>
minimum_daily_calories: <number-or-blank>
macro_target_protein_g: <number>
macro_target_fat_g: <number>
macro_calorie_tolerance_kcal: <number>
```

`minimum_daily_calories` is optional. A blank value means that the common-sense recommendation is unavailable; AI System must not invent a minimum.

## Daily Summary Food Schedule

When the local configuration contains a complete macro food-block schedule, the daily summary shows the IF window followed immediately by six owner-defined food blocks:

```text
09:00-11:00
11:00-13:00
13:00-15:00
15:00-17:00
17:00-19:00
19:00-21:00
```

The calculator returns the blocks under the `food_blocks` JSON key. Each block has `configured` or `empty` status. Configured blocks report derived calories, protein, fat, and carbohydrates. Empty blocks report no numeric values and do not count as intake. The selected schedule is determined by planned training/rest mode: complete training data selects `training`, explicit no-training selects `rest`, and missing or ambiguous data remains `unknown`. The independent `planned_calories_representative` value supplies the total calorie target. If the calorie target or selected profile is missing, the schedule is `unknown` or `unavailable` and the calculator does not guess. For a selected profile, IF conflicts are returned as `if_conflicts`.

Configuration uses shared targets `macro_target_protein_g`, `macro_target_fat_g`, and `macro_calorie_tolerance_kcal`, plus `macro_training_block_<slot>_*` and `macro_rest_block_<slot>_*` keys. Each block has a `status` and, when configured, approximate `protein_share_percent`, `fat_share_percent`, and `carbohydrates_share_percent`. The calculator allocates the shared protein and fat anchors by those shares and calculates carbohydrates as the residual required by the check-in calorie target. The training/rest standards remain owner baselines for reporting and do not set the calorie target.

The summary compares the primary daily calorie target with calories derived from macro grams using `4/4/9`, and with the sum of block calories. It reports differences without changing the target or macro values. The sum of blocks must remain within the configured calorie tolerance, normally `±90 kcal`; protein and fat totals must match their configured anchors, while carbohydrates remain residual. If a configured block falls outside the IF window, the conflict is shown. Missing or incomplete macro configuration makes the food schedule unavailable while leaving the spending and weekly calorie report usable. The unavailable result contains a deterministic `reason` and `invalid_or_missing_fields`, and never exposes partial macro values. Missing or malformed base budget configuration, missing private configuration, or stale official indexes remains a calculator `STOP`.

## Monthly Spending

For a report date `D` in the configured timezone:

- calculations use only indexed records whose `session_date` is on or before `D`; a later check-in may close `D`, but it must not retroactively change a historical plan projection rendered for `D`;
- `current_spending` is the sum of `previous_day_finance_amount` for indexed closure dates in the current calendar month through `D`;
- `remaining_base_budget = monthly_base_budget - current_spending`;
- `remaining_days_inclusive` includes `D` and all later calendar days in the month;
- `average_available_per_remaining_day = remaining_base_budget / remaining_days_inclusive`;
- `cumulative_pace_target = daily_spending_pace * calendar_day_number(D)`;
- `pace_overrun = max(0, current_spending - cumulative_pace_target)`;
- `no_spend_days_after_today = ceil(pace_overrun / daily_spending_pace)`;
- `no_spend_days_from_today = no_spend_days_after_today + 1` when overrun is positive, otherwise `0`;
- `standard_spend_resume_date = D + no_spend_days_from_today` when overrun is positive, otherwise `D`.

The configured buffer is reported separately. It does not silently increase the operational base budget. Approximate source amounts make the derived figures approximate.

## Weekly Calories

Each reporting week is Monday through Sunday. Saturday and Sunday from the previous week are never included in a new weekly balance.

- the report is an `as-of D` projection and uses only records available by `D`, identified by `session_date <= D`;
- actual consumed calories come from indexed closure properties whose `closure_date` is in the current Monday-Sunday week;
- the current planned calorie value is shown separately and may be used for projection;
- `projected_remaining_after_today = weekly_calorie_budget - actual_consumed - planned_today`;
- `mechanical_limit_after_today = projected_remaining_after_today / remaining_days_after_today` when future days remain;
- `mechanical_limit_inclusive = (weekly_calorie_budget - actual_consumed) / remaining_days_inclusive`;
- the configured training/rest standards are displayed as owner baselines;
- `common_sense_limit = max(mechanical_limit_after_today, minimum_daily_calories)` only when the minimum is configured;
- if the minimum is blank, common-sense recommendation and unbalanced balance are `unknown` rather than invented.

When the configured minimum prevents closing the weekly budget, report the remaining amount as `unbalanced_balance` for later days or weeks. The calculator must not prescribe a lower limit or interpret health effects.

## Post-Write Use

After a successful daily check-in write or update, the route must:

1. save the canonical Markdown and optional assets;
2. run the real `.systems/scripts/sync-personal-ops-check-ins-v4 --post-write` refresh in unified workspaces or for native V4; only unmigrated V3 uses `.systems/scripts/sync-personal-ops-check-ins-v3 --post-write`;
3. read the refreshed official indexes;
4. calculate the owner-only budget projection for the response summary.

`--status-only` is diagnostic only and is not a valid post-write refresh. If refresh fails, the canonical check-in remains durable, but the response must report the partial result and failed refresh. It must not claim current indexes or full validation success.

## Privacy

Budget and calorie outputs are owner-only, `private-sensitive`, and chat-only unless separately approved. They must not enter sanitized trends, Dreaming Mode, memory, System Insights, External Memory, skills, or public/project artifacts.
