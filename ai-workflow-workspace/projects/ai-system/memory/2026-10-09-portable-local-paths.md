# Portable Local Paths

- Type: project-constraint
- Status: active
- Source: CR-011 recovered architecture/plan/spec, current task quality and accepted distillation

Only HOME, AI_SYSTEM_HOME and selected AI_SYSTEM_WORKSPACE_HOME are expanded in supported local root fields. Values resolve to absolute lexical paths with explicit relative bases, rejecting symlink components before normalization. Raw configuration stays unchanged; tasks are Markdown files and TaskForge remains optional UI. Missing repositories report pending availability and blocked execution.

New Work Evidence preparations use transaction schema 2 and hash-covered path_context schema 1 (workspace, source aliases and ordered ledger roots). Apply/recover/prepare dedup must match the fresh resolved context. Schema-1 literal-root replay remains supported; dynamic-root replay fails closed. Integrity reads preserve original schema/hash/chain and do not require old host roots to equal current roots. No historic context backfill or data migration.

Before live adoption, address pending transactions under original approved contexts. After V2 preparations use compatible readers or forward fixes; old readers cannot safely replay them. Mac path behavior is simulated, not a real Mac execution. Product code is in the CR-011 isolated codex worktree; deployment, publication, management update and old Capture repair are separate scopes. A target-product commit requires fresh current-HEAD QA.
