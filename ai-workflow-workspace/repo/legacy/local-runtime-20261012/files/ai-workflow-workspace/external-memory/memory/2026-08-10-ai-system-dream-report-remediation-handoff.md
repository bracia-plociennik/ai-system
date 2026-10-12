# AI System Dream Report Remediation Handoff

## Metadata

- Date: 2026-08-10
- Owner decision: yes
- Counterpart: AI Workflow
- Handoff artifact: this file
- Scope: privacy-safe transfer of validation and evidence-contract decisions
- Source systems: AI System and AI Workflow

## Outcome

AI System remediation requires workflow evidence that can be scoped to one project without weakening the global
workflow validator. The counterpart workflow now documents and implements an optional `--project <safe-slug>` selector
for status and QA-evidence checks. Product contract validation remains global.

## Decisions And Boundaries

- Project-scoped validation is an evidence-selection tool, not a bypass for global contract checks.
- Historical QA remains immutable. Pre-contract evidence requires an exact workspace-relative path and SHA-256.
- Incomplete current-contract evidence may be superseded only by a separately fingerprinted recovery artifact that passes
  the current contract; the original is not upgraded into PASS evidence.
- A legacy Dream Report may bypass only current structural-section checks when admitted by an exact path and SHA-256
  registry entry. Privacy and secret scanning remain mandatory.
- AI System validation scripts emit completion/evidence markers as supporting evidence; semantic PASS remains separate.

## Source References

- AI System product contracts: `.systems/ai/core/validation-routing.md`, `.systems/ai/core/validation-profiles.md`,
  `.systems/ai/core/dreaming-mode.md`
- AI System validators: `.systems/scripts/validate-ai-system`, `.systems/scripts/check-dreaming-mode`
- AI Workflow counterpart: `ai-workflow/.systems/scripts/validate-workflow`,
  `ai-workflow/.systems/scripts/check-status-consistency`, `ai-workflow/.systems/scripts/check-qa-evidence`
- Evidence contracts: `ai-workflow/.systems/ai/core/full-qa-verification.md`

## Validation Expectations

- Scoped AI Workflow checks must preserve selected-project failures.
- Global AI Workflow validation may still report unrelated workspace drift; report that separately.
- AI System Dream Report registry entries must be exact path/fingerprint pairs.
- No runtime client data, secrets, private identifiers, raw exports, or production details are transferred by this handoff.

## Adaptation Checklist

- [x] Project-scoped workflow validation is documented.
- [x] Historical QA recovery disposition is documented.
- [x] AI System legacy Dream Report admission is documented.
- [x] Validator completion evidence is documented as supporting-only.
- [ ] Owner review of final findings and commit scope remains required.

## Privacy And Residual Risk

- Privacy check: passed for this handoff; no client, personal, credential, or production data is included.
- Residual risk: global workflow health may remain noisy because unrelated projects are intentionally not hidden.
- Residual risk: script markers prove execution completion, not semantic correctness or final acceptance.
