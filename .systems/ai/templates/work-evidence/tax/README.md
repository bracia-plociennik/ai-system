# Private Evidence Register

No taxpayer inference or automatic init. Configure an explicitly approved existing
workspace/private-tax/taxpayer-id/config.json. Required fields: schema_version=1,
taxpayer_id, owner_workspace, currencies (explicit PLN/EUR/USD), source_roots
(aliases to relative directories under the taxpayer root), allowed_workspaces
(IDs to absolute local operational workspace roots).
The taxpayer directory must already be owned by the current local user with no
group/other access (for example mode 0700). The tool never changes permissions.

Bundle requires taxpayer_id, tax_year, ip_items, rights, finance, allocations and
work_refs. See work_evidence_tax_evidence.py for strict field contracts. Amounts
are nonnegative Decimal strings or null for unknown source amounts. Negative
credit corrections require a later approved policy; they are not guessed here.
Source refs: root_alias, relative_path, sha256, observed_at, evidence_state
(asserted, verified, advisor-assessed). These labels are assertions, not automatic
legal proof. IP, taxpayer, client and domain identities are separate.

Work refs bind owning workspace, entry ID/hash and optional documented kit hash.
No time is copied. Allocations reference those owner:entry-id keys and cannot
exceed source amounts. Missing rights/amounts or conflicts block completeness.

preview is read-only; write requires --owner-approved and --expected-hash.
Packets stay private. Evidence-only never means qualified IP or computed tax.
No rules are adopted from examples, historical percentages or filenames.

## Calculator Rules
work-evidence-tax-calculate preview/write/read uses a relative private rules JSON.
The envelope has schema_version, rule, approval, revoked, synthetic, activation.
The rule declares IDs/version/taxpayer/year, effective_start/end_exclusive,
currency, precision (28-50), places (0-8), rounding (half-up/half-even/down), scope,
qualification_method, allocation_method, exclusions, inputs, expressions,
outputs and reference_cases. Inputs explicitly map names to finance_id,
field (amount/allocated), unit (money). No arbitrary executable formulas.
Expressions: const(value/unit), ref(name), or op+args. Operations add/sub/mul/div/
sum/ratio/min/max are bounded; no eval, code strings, money*money, zero or negative
denominators. Units are money in the declared currency or dimensionless ratio.
Golden cases provide every input Decimal string and every expected output value;
all must match declared rounding. All nodes, including unused nodes, are checked.

Approval: rule_hash, advisor_id, approved_at, private source_ref, owner_verified.
These are explicit human evidence assertions, not independent signature checks.
synthetic=true requires activation=null and emits synthetic_nonlegal=true.
Real activation additionally binds rule_hash/taxpayer_id/approved_at/approved_by
owner/advisor_reviewed=true; no such real rules are supplied by this product.
All source evidence must be complete; no partial tax output. Results stay draft
and private. Write requires owner approval and expected result hash; current read
recomputes all bindings and marks changed/revoked results stale. No filing.
