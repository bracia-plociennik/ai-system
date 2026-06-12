# System Insights

## Purpose

System Insights are anonymized, operational lessons extracted from completed work so future projects, reviews, offers, processes, and skills can improve without carrying raw client or project data forward.

They live inside the selected workspace:

```text
AI_SYSTEM_WORKSPACE_HOME/system-insights/
  README.md
  system-insights.md
  insights/
    README.md
```

System Insights are advisory. They do not override `AGENTS.md`, `.systems/ai/core/`, workspace status, memory, decisions, checkpoints, privacy rules, validation, stop conditions, owner approvals, or skills.

## Scope Boundaries

| Memory level | Scope | Use for | Do not store |
| --- | --- | --- | --- |
| External Memory | AI System product improvement | proposed changes to AI System rules, templates, validators, scripts, docs, or system skills | product-domain lessons, client collaboration lessons, workspace facts, project facts, raw client data |
| System Insights | anonymized cross-project operating lessons | frontend, backend, smart contracts, SEO, ads, offer, process, quality, client-work, product, and skill-candidate lessons | raw client data, client names, secrets, repo-specific facts, project-specific details |
| Workspace Memory | one selected workspace | broad workspace facts, preferences, operating notes, and decisions | anonymized cross-domain lessons without workspace relevance, system improvement proposals |
| Client / Owned-Asset / Project Memory | one private client, asset, or project | raw local facts, decisions, constraints, implementation notes, risks, and watch items needed by later work | generalized skill material without local relevance, system improvement proposals |

## Categories

Use one primary category per insight and optional secondary tags only when needed:

- `frontend`
- `backend`
- `smart-contracts`
- `seo`
- `ads`
- `offer`
- `process`
- `quality`
- `client-work`
- `product`
- `skills`

## Status Values

- `proposed` - candidate captured but not accepted as a reusable operating lesson.
- `accepted` - reviewed and safe to reuse as advisory context.
- `promoted-to-skill` - converted into a workspace or system skill through the relevant skill workflow.
- `superseded` - replaced by a newer insight or skill.
- `rejected` - intentionally not reused.

## Write Policy

Agents may propose a `System Insight Candidate` during distillation, checkpoint review, QA/review, guide mode, task-intake, or owner-approved capture.

Agents must not write durable System Insights ad hoc during active implementation.

Durable writes to `AI_SYSTEM_WORKSPACE_HOME/system-insights/**` are allowed only when one of these is true:

- a checkpoint atomically writes an accepted insight from source-backed distillation;
- final review records an owner-approved capture or verifies existing entries;
- the owner explicitly requests and approves a capture task with exact write permission.

When multiple projects produce related lessons, aggregate them through checkpoint or an owner-approved capture task instead of duplicating entries.

## Privacy And Anonymization

Every System Insight entry must include a privacy check.

Before writing an insight:

- remove client names, personal names, company names, emails, phone numbers, wallet addresses, account IDs, ticket IDs, exact domains, exact repository names, and production identifiers unless they are public generic technology names;
- remove `.env` content, credentials, API keys, private keys, seed phrases, access tokens, production credentials, internal URLs, and security-sensitive operational details;
- convert project-specific implementation details into generalized conditions, decisions, and reusable rules;
- keep only source scope labels such as `project distillation`, `checkpoint`, `QA review`, or `owner-approved capture`;
- mark uncertain or non-reusable material as rejected or leave it out.

If anonymization would remove the operational value, do not write the insight.

## Entry Contract

Each detailed insight entry should be written as:

```text
AI_SYSTEM_WORKSPACE_HOME/system-insights/insights/YYYY-MM-DD-short-kebab-title.md
```

Use `.systems/ai/templates/workspace/system-insights/system-insight.template.md`.

Each entry must contain:

- `TEMAT`
- `0. SYGNAŁY`
- `1. CO ZOSTAŁO FAKTYCZNIE ZROBIONE`
- `2. PROBLEMY (→ KONWERSJA)`
- `3. WZORCE`
- `4. DECYZJE`
- `5. ZASADY NA PRZYSZŁOŚĆ`
- `6. OTWARTE LUKI`
- `7. ODRZUCONE JAKO SZUM`
- `8. WALIDACJA OPERACYJNA`
- privacy check
- source scope
- skill candidate: `yes|no`
- suggested skill target

`8. WALIDACJA OPERACYJNA` must include:

- `co zostaje`
- `co poprawić / usunąć`
- `czego brakuje`

If there is no additional useful validation, write `BRAK DODATKOWEJ WALIDACJI`.

## Promotion To Skills

An insight is a skill candidate when it describes a repeatable method, checklist, review heuristic, implementation pattern, or evaluation rubric that can be applied across future work.

Promote to a skill only through the normal skill creation/update process. System Insights can suggest a skill target, but they do not automatically create or change skills.

Good promotion candidates:

- repeated frontend quality heuristics;
- backend architecture review checklists;
- smart contract safety review procedures;
- SEO or ads operating playbooks;
- client collaboration role patterns;
- QA rubrics that reduce repeated failures.

Weak promotion candidates:

- one-off project facts;
- subjective preferences without evidence;
- lessons that still depend on raw client context;
- implementation notes that belong in project, client, owned-asset, or workspace memory.

## Validation

Use `.systems/scripts/check-system-insights` to validate required policy/templates, insight entry structure, privacy checks, raw data markers, and External Memory scope separation.
