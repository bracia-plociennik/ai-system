# Branch Promotion

## Purpose

This document records the branch-promotion rule used to create the dedicated `ai-system` branch from the staged project implementation.

The current branch is already promoted. Use this file only when repeating or auditing that migration pattern.

## Promotion Steps

1. Create or checkout the dedicated `ai-system` branch.
2. Move contents of staged `ai-system/` to branch root.
3. Rename `agents.template.md` to `AGENTS.md`.
4. Rename `humans.template.md` to `HUMANS.md`.
5. Keep private workspace runtime ignored. Legacy branch promotion used `ai-system-workspace/`; multi-workspace installations also ignore registered workspace roots.
6. Run all validators before commit.

Do not perform future branch promotion before final check and owner approval.
