# Naming consumer scope

`check-naming` checks product Markdown from the live filesystem and Git index,
then current managed Markdown in an explicitly selected workspace. Absolute
workspace paths are normalized relative to each governing owner. No source file
is renamed, migrated or rewritten by this read-only consumer.

Product root `AGENTS.md` and `HUMANS.md`, `README.md`, the generated root contract
template and canonical active `<skill>/SKILL.md` are exact exceptions. Workspace
active skills use `skills/<slug>/SKILL.md` in the workspace, nearest client or
owned-asset namespace. Other uppercase contracts in managed runtime still fail.
Skill raw `context/` and product legacy skills retain their original filenames.

Per workspace or client/owned-asset owner, `projects/`, `context/`, `documents/`,
`contracts/`, `assets/`, `archive/` and `dump/incoming/` contain source inputs,
not System-generated naming targets. Project source naming belongs to its own
repository. Canonical status, memory, notes, decisions, task, QA, Capture and
skill resource paths remain checked; whole client or project-state namespaces
are never exempt. Project-state work-unit `backups/`, `router-backups/`, `tests/`
and canonical Capture `history/` preserve original evidence filenames. Links
are rejected rather than followed, including links into an excluded source slot.
Unknown paths otherwise retain strict naming checks.

Existing Personal Ops V4 generation/compatibility links are the one managed
link exception: exact `personal-ops/indexes/check-ins-v4-active` with a contained,
unlinked `generations-v4/<24 hex>` directory, and the six exact stable filenames
declared in `personal-ops-aggregates-v4.md` pointing through that pointer. The
consumer does not follow these aliases; it checks generation filenames directly.
Generation content/freshness remains owned by its existing aggregate consumers.

Task-management's exact `tasks/TaskForge.md` and title-based
`tasks/TaskNotes/Tasks/*.md` follow their existing filename contract. Task and
Personal Ops archives, plus original task snapshots under migration-report
`backups/`, `removed-tasknotes/` or `active-folder-originals/`, are preserved
sources. Newly generated migration reports and other task metadata stay strict.
Weekly planning and SPOR use their exact `YYYY/YYYY-Www.md` routes under
`tasks/weekly-plans/` and `personal-ops/weekly-check-ins-v4/`; the year must match
the filename and the ISO week must exist. Arbitrary uppercase week-like names
elsewhere retain ordinary naming checks.

## Historical loose root inputs

An optional local `core/naming-source-preservation.json` admits only exact
noncanonical loose root Markdown sources with matching historical Git bytes:

```json
{"schema_version": 1, "inputs": [
  {"path": "Historical input.md", "sha256": "<64 lowercase hex characters>",
   "source_commit": "<40 lowercase hex characters>",
   "disposition": "preserved-unclassified"}
]}
```

Creation requires owner-approved preservation scope and explicit historical
provenance. This registry cannot exempt managed status/QA/Capture, root routers,
active contracts, directories, wildcards or arbitrary new inputs. Duplicate,
linked, malformed, stale, absent or altered records fail closed. Every admitted
input is visibly reported as historical and unclassified; admission neither
classifies its owner/content nor grants current quality, migration or naming
approval. Changed bytes require a fresh scoped decision, not automatic re-pinning.
Private names and provenance stay in the selected workspace, never the product.
