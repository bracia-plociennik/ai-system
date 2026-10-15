# System And Workflow Authority

## One work lead and one procedure

AI System is the owner's superior personal coordination system. AI Workflow owns project execution, risk, phases, task state, QA and technical capture under that coordination. A work lead is human or the owner's scoped AI System delegate. Equal authorized scope and evidence yield equal permitted actions through the same procedure; actor type alone never adds an owner question. Auto/Human interaction modes remain independent.

System chooses goals, priority, supported execution policy and covered decisions. Workflow follows covered directions and returns actual evidence or specific blockers to the lead. The same session can occupy both roles. No second coordinator process, scheduler, approval store or technical status is introduced.

## Rule classes and precedence

Platform/tool restrictions apply first. Actual current owner decisions and reservations govern System, which governs configurable Workflow policy. Factual repository truth and required quality remain independently assessed.

| Class | Examples | Required behavior |
| --- | --- | --- |
| owner-reserved | grant/extend/revoke delegation; change reservations; actual final-owner-yes | actual specific owner decision |
| evidence/safety invariant | actual QA/tests, privacy, required risk/phase floors, tool restrictions | cannot override/relabel/fabricate |
| configurable execution policy | covered task choice, supported route, task-local interaction, in-scope technical choice | follow verified System direction even when local configurable default differs |
| unknown | ambiguous conflict or unsupported consumer | block affected action, return exact reason to lead |

Policy changes themselves follow approved development/installation, not runtime exceptions. Existing installations retain current gates until a compatible reviewed update. Reuse a high-risk approval already covering the action and formal assessment for either lead; new actions/resources require coverage.

## Work-lead envelope v1

Extend an existing owner orchestration/task record, not a second approval database. Required work_lead fields: schema_version=1, lead_id, lead_kind (human|ai-system), owner_id, parent_work_id, mandate_ref, mandate_revision, allowed_actions, resource_roots, phase_ceiling, reserved_actions, escalation_target.

Closed action vocabulary: inspect, planning-artifacts, implementation, quality-assessment, local-commit, publish, install-activate, external-effect. Each action needs concrete approved resources. No wildcards or unknown fields/actions widen scope. Effective scope is owner mandate AND current request AND phase gates AND verified roots AND platform allowance. Later narrower owner instructions win. Mandate evidence includes original owner instruction reference, issued/revoked/superseded disposition, limits and trusted owning namespace. Non-expiring is explicit, never invented expiry.

Schema validation proves only structure/scope consistency, never authenticity. Executing agent checks the actual trusted conversation or owner-approved durable evidence and current revocation disposition. A repository approved=true, generated envelope, agent-created HMAC, hash, stale cache or peer assertion cannot authenticate consent. Missing/unverifiable evidence is unknown. Resume/tool changes preserve stable parent and limits and recheck disposition.

## Consumer and escalation

Extend existing coordinator status only with an explicitly selected new schema/capability; old default readers stay unchanged. Fields: lead_contract_version, context_binding, authority_check (matched|missing|expired|revoked|out-of-scope|unknown), actual_gate, actionable_blockers, evidence_refs, next_allowed_action. Every read-only report has execution_authorized=false, even when scope metadata matches.

System resolves covered decisions; only uncovered/owner-reserved decisions reach owner. Required QA failure cannot be overridden by either lead. Unbound standalone Workflow follows its ordinary human-led procedure. A task bound to unavailable/incompatible System permits inspection but blocks dependent execution. Explicit detach/rebinding retains history and requires real scope review.

## Compatibility and evidence

Contract version differs from installed revision. Reject unknown major/fields and verify source consistency; labels alone do not prove support. Roll out compatible Workflow consumer, then System producer, then approved adapter activation. Preserve historical QA unchanged; current claims require applicable current evidence. No history migration, broad filesystem permission or automatic project enrollment. Codex is the current native acceptance target; Claude/other providers remain documented MVP design/interface until independently verified.
