# Branch Promotion

## Purpose

This document records the branch-promotion rule used to create the dedicated `ai-system` branch from the staged project implementation.

The current branch is already promoted. Use this file only when repeating or auditing that migration pattern.

## Promotion Steps

1. Create or checkout the dedicated `ai-system` branch.
2. Move contents of staged `ai-system/` to branch root.
3. Move the agent contract into `.systems/ai/templates/root/AGENTS.template.md`.
4. Rename `humans.template.md` to `HUMANS.md`.
5. Generate local root `AGENTS.md` with `.systems/scripts/init-ai-system`.
6. Keep root `AGENTS.md` and private workspace runtime ignored. Legacy branch promotion used `ai-system-workspace/`; multi-workspace installations also ignore registered workspace roots.
7. Run all validators before commit.

Legacy promotions may have renamed `agents.template.md` directly to tracked `AGENTS.md`. Current AI System keeps `AGENTS.md` local-only and commits only its root template.

Do not perform future branch promotion before final check and owner approval.
