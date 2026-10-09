# Branch Promotion

## Purpose

This document records the historical pattern for promoting a staged project implementation into a repository root. It does not prescribe a branch name or define a checkout role.

The product files already live at the repository root. Use this file only when auditing that historical migration pattern, not for normal installation or updates.

## Promotion Steps

1. Select the owner-approved migration branch explicitly.
2. Move contents of staged `ai-system/` to branch root.
3. Move the agent contract into `.systems/ai/templates/root/AGENTS.template.md`.
4. Rename `humans.template.md` to `HUMANS.md`.
5. Explicitly bootstrap a management checkout with `.systems/scripts/init-ai-system --role management`; development preserves its own local contract.
6. Keep root `AGENTS.md` and private workspace runtime ignored. Legacy branch promotion used `ai-system-workspace/`; multi-workspace installations also ignore registered workspace roots.
7. Run all validators before commit.

Legacy promotions may have renamed `agents.template.md` directly to tracked `AGENTS.md`. Current AI System keeps `AGENTS.md` local-only and commits only its root template.

Do not perform future branch promotion before final check and owner approval.
