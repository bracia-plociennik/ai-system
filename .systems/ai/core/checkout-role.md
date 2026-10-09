# Checkout Role

## Local Configuration

The local-only, ignored `ai-system.local.json` is the explicit checkout role.
Its exact schema is `{"schema_version": 1, "role": "management"}` or
`{"schema_version": 1, "role": "development"}`. Duplicate, unknown, missing
or wrong-type keys, unknown roles and linked files fail validation.
Do not commit a populated role record. The product ships only a neutral template.

The role is independent of Git branch, basename, remote and installation layout.
`ai-system-dev` describes the owner's product-development checkout, not a required
directory name on other machines. Read-only intake may proceed without a record;
implementation-class writes require a resolved role and applicable local contract.
Configuration is not authority, owner approval, security isolation or proof of
Workflow installation, workspace readiness or QA. Existing gates remain mandatory.

## Explicit Bootstrap

First run requires `.systems/scripts/init-ai-system --role management` or
`--role development`. No-role initialization without a record stops before writes.
Subsequent no-role invocation reuses the validated local record. A conflicting
`--role` stops; role changes and contract reconciliation are separate owner-approved
work, not an implicit migration. Existing installations are not backfilled.

- Management generates missing `AGENTS.md` from the committed management template.
  Existing recognized generated contracts are preserved unless `--refresh-agents`
  is explicit. Unrecognized contracts require clarification, not implicit overwrite.
  A Workflow shim cannot be overwritten by management bootstrap, even with refresh.
- Development preserves an existing project AGENTS byte-for-byte, never generates
  the management contract and rejects `--refresh-agents`. A management-generated
  AGENTS is a conflict, not a usable development contract. Missing development
  AGENTS is reported as not ready; bootstrap records role only, without claiming
  that product work can start or installing Workflow.
- Configuration, contracts and output paths are preflighted before writes.
  Linked output/template/configuration paths fail. Successful bootstrap is
  idempotent; failed preflight does not leave partial files. Unexpected filesystem
  failures are reported; bootstrap is not a multi-file transaction or concurrency
  lock. Do not run two bootstrap writers on the same checkout.
- `--status` is read-only JSON: configured role (or unconfigured), contract state
  and ready status. Missing configuration is unconfigured, not management by guess.
  Invalid configuration or role/contract conflict exits nonzero. Missing contract
  reports not ready, not a product verdict.

## Workflow Boundary

Product branch/worktree and filtered release rules live in `product-publication.md`.
Develop on `dev`; feature worktrees start from current dev, publication worktrees
from current main. This does not change checkout-role validation or write gates.

Management does not require AI Workflow in its own root. A managed project using
Workflow must satisfy its installed local project-orchestration preflight. The
development role likewise does not install, initialize or upgrade Workflow.
Never refresh a development project's AGENTS from the management template.

## Verification

`check-checkout-role` checks this contract, bootstrap consumers and synthetic
behavior tests. It does not change configuration or AGENTS, scan private runtime,
create workspaces or grant write authority. Green scripts are supporting-only.
