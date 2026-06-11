# AI System Workspaces

## Purpose

Local-only registry for private AI System workspace roots under one `AI_SYSTEM_HOME`.

Keep this file at repository root as `ai-system-workspaces.md`. It is ignored by git and must not contain secrets, credentials, private documents, or detailed client facts.

## Registry

| workspace-id | path | default | status | scope | notes |
| --- | --- | --- | --- | --- | --- |
| `<workspace-id>` | `<workspace-directory>/` | `yes` | `active` | `<scope>` | `<short routing note>` |

## Field Rules

- `workspace-id` - lowercase kebab-case id used in prompts and routing.
- `path` - root-relative or absolute path to the private workspace.
- `default` - `yes` for exactly one default workspace, otherwise `no`.
- `status` - `active`, `paused`, `archived`, or `planned`.
- `scope` - short routing class such as company, private, clients, owned-assets, or project family.
- `notes` - short non-sensitive routing note only.

## Selection Rules

1. Explicit workspace id or path in the owner prompt wins.
2. `AI_SYSTEM_WORKSPACE_HOME` wins when no explicit workspace is provided.
3. Registry `default=yes` wins when no explicit or environment selector is present.
4. If multiple workspaces plausibly match, stop and ask the owner to choose.
