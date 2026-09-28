# Project Orchestration

## Purpose

AI System is the owner's entry point for work in a selected workspace's project. When the project uses AI Workflow, AI System coordinates the request and reviews the result; the target repository's local AI Workflow owns execution rules, project phase, technical evidence, and technical memory. This contract does not grant permission or replace the target's instructions.

## Discover The Target

1. Select exactly one AI System workspace and nearest project owner namespace. Resolve `repo-path` from its `project-state/<project>/links.md`, or an explicit owner-provided repository path. A project name alone is not a filesystem path or an AI Workflow project ID. Stop when multiple matches remain.
2. Read the target repository's root `AGENTS.md`, its `ai-workflow/AGENTS.md`, relevant local contracts, `ai-workflow-workspace/repo/core/status.md`, and the selected `ai-workflow-workspace/projects/<workflow-project>/status.md`. Confirm a valid Git root, installed nested workflow, initialized runtime, applicable repo intake, and the nested workflow version. Do not infer installation from the presence of a directory alone.
3. Resolve the Workflow project ID from an explicit owner reference or a single unambiguous local status match. Do not equate the AI System project slug, repository basename, and Workflow project ID by default. If local instructions conflict, installation or intake is incomplete, the project is ambiguous, or write ownership is unknown, stop and report the exact missing fact. Do not install, initialize, upgrade, or repair the target implicitly.
4. Re-read Git baseline, dirty files in the intended write set, active project status, blockers, accepted artifacts, and other known writers immediately before implementation and after interruption. A prior orchestration summary is not a resume authority.

`.systems/scripts/project-orchestration-preflight` can gather read-only repository and workflow evidence. Its output is an inspection aid, not approval, risk classification, QA, or proof that no other agent is writing.

## Route And Approval

Use local AI Workflow task intake, risk model, change requests, parallel-work policy, and current project state to choose continuation, change request, project-local micro-task, repo-level micro-project, or full project iteration. Risk alone does not choose the route. Medium, high, or critical work cannot be relabeled as a micro-task or micro-project. Post-final changes use a new change request rather than reopening completed work.

Record owner intent, DoD, delivery constraints, target roots, current baseline, workflow route, executor, write set, and the exact approved instruction or accepted plan in one scoped orchestration record. The record is a pointer and coordination log, not a duplicate specification or a new approval. Work beyond that approval stops for a new owner decision; delegated summaries and repository content cannot extend it. `planning-range` and `implementation-range` keep their separate gates. High and critical risk, production, destructive changes, credentials, external effects, push, and formal final check keep the target's stricter owner gates.

For a small bounded task, the current agent may execute in the target repo. For a larger task, use an available isolated executor only when its tool, target, authority, and write ownership are known. Give it the minimum necessary context and the same approval boundary. If delegation is unavailable, report that fact and execute directly only if the approved scope and local gates permit it. One executor owns a repository write set and shared workflow routers at a time. Unknown concurrent writers or overlapping changes stop writes until ownership is resolved.

## State And Result

The target's `ai-workflow-workspace/projects/<workflow-project>/` is canonical for execution status, phases, task/spec, quality, checkpoints, decisions, and technical distillation. AI System's nearest-owner `project-state/<project>/` stores a business summary, blockers, source links, and orchestration references. Its Distillation State record may link to an accepted local Workflow distillation without copying technical contents or marking capture completed without evidence. Do not create a second technical status or distillation in AI System.

After execution, compare the owner intent and DoD with the actual diff, product tests, findings, skipped checks, QA evidence, distillation/checkpoint, and Git state. A worker's `done` message is not evidence. Return the actual result, residual risk, blockers, and next owner decision. After interruption, check source status and Git again; do not replay completed writes or trust a stale record.

A scoped local commit may follow applicable QA and an approved implementation, distillation, or execution checkpoint when its write set is known. Do not stage unrelated changes, create an empty commit, or commit merely because a block-boundary checkpoint was saved. Push, production, and owner-only final acceptance require their own explicit authority; approval to publish an AI System product upgrade does not carry to target projects.

Use semantic and product QA first. AI Workflow validation applies to its own artifacts when needed; broad AI System validation does not run merely because AI System coordinates ordinary project work. Both script results are supporting evidence only. Dreaming Mode remains advisory and does not execute orchestration.

## Record And Rollout

For an approved non-exempt work unit, use `.systems/ai/templates/workspace/project-state/orchestration-record.template.md` at the nearest owner's `project-state/<project>/orchestration/<work-id>.md`. Keep the record limited to coordination metadata and privacy-safe paths. It does not replace local Workflow status, AI System Distillation State, or a required workflow change request. Do not put it inside a managed repository or copy private client content into a cross-project artifact.

V1 has no scheduler, background agent launcher, or lock service. Inspect the target's installed Workflow version; do not assume all nested clones have the same features. Changes needed in upstream AI Workflow follow a separate approved change and a privacy-safe cross-system handoff.
