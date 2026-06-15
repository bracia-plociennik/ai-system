# update-from-upstream

## Purpose

This contract separates AI System product updates from private workspace schema backfill.

`update-from-upstream` updates system-owned repository files.

`update-workspace` backfills missing neutral runtime workspace schema files after the system has been updated.

## Boundaries

`update-from-upstream` may update only system-owned files in the AI System repository:

- `.systems/**`;
- validators and scripts;
- templates;
- `README.md`;
- `HUMANS.md`;
- root agent contract template.

It must not modify private runtime workspaces, `ai-system-workspaces.md`, client data, project data, project-state entries, memory, checkpoints, system insights entries, external memory entries, or `.git/info/exclude`.

`update-workspace` may create only missing neutral workspace directories, routers, README files, and template files inside an existing selected workspace. It must not overwrite existing files.

## Recommended Update Flow

After a successful upstream update, run:

```text
.systems/scripts/update-workspace --dry-run
.systems/scripts/update-workspace
```

When `ai-system-workspaces.md` contains multiple workspace rows, use:

```text
.systems/scripts/update-workspace --all --dry-run
.systems/scripts/update-workspace --all
```

## update-workspace Rules

Use:

```text
.systems/scripts/update-workspace [--workspace <path-or-id>] [--workspace-profile <auto|generic|primary-entity>] [--all] [--dry-run]
```

Selection without `--all` follows normal AI System workspace selection:

1. `--workspace <path-or-id>`;
2. `AI_SYSTEM_WORKSPACE_HOME`;
3. registry row with `default=yes`;
4. legacy `ai-system-workspace/`.

`--all` reads `ai-system-workspaces.md` and updates existing workspaces with `status=active` or `status=paused`. It reports `planned`, `archived`, and missing workspace paths as skipped.

`update-workspace` is not a fresh bootstrap tool. If the selected root workspace does not exist, stop and run `.systems/scripts/init-workspace` first.

`--dry-run` must not write files. Normal mode must preserve every existing file and end with:

```text
No existing workspace files were overwritten.
```

Do not create `prompting/` by default. Prompting artifacts require exact owner-approved scope.
