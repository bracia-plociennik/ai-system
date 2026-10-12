# Unified Aggregate Architecture, Plan And Specification

Source: owner-approved mapping and cutover plan in this chat, 2026-10-01. Classification: implementation-capable. Implementation writes planned: yes, upstream product, scoped workflow evidence and selected private aggregate runtime.

## Architecture And Mapping

Canonical Daily/Weekly schema stays unchanged. Aggregate contract `personal-ops-aggregate-v4-v1` wraps properties with source version, per-field confidence, mapping dispositions and dated normalized observations. All V3 schema fields and V4 schema/known additive fields are accounted for. Raw, OCR, attachment payloads and dump content are excluded. Unknown nonempty fields stop build; known structured JSON is preserved with its provenance. Older archive CSV enrichment uses an explicit allowlist, source-path matching and separate legacy extensions; presence flags and subjective descriptions never become completed outcomes or numeric ratings.

Immutable index generations contain JSONL, CSV, metrics, dictionary, sanitized trends, router and hashed manifest. An atomically replaced directory symlink `personal-ops/indexes/check-ins-v4-active` selects one complete generation. This single filesystem pointer replaces the proposed JSON pointer so human-facing export links and product readers use the same atomic operation. Unmigrated workspaces retain existing behavior. Source hashes and inventories detect same-count edits and additions. A shared writer lock covers migration and sync. Imported history is an immutable private input, refreshed native canonical properties remain authoritative; source changes stop rather than silently freeze history.

Budget observations distinguish dated values, intervals and multi-day aggregates; conflicting values fail rather than double-count. Imported defaults marked unknown are not observed zeros. Weekly stays a distinct canonical projection, never a second daily fact stream. Life Alignment still uses owner-authored canonical answers. Aggregate records cannot authorize TaskNotes.

## Implementation Slice Plan

| Slice id | Goal | Expected files/areas | Acceptance check | Evidence required | Status |
| --- | --- | --- | --- | --- | --- |
| S1 | loss-accounted adapter and source inventory | aggregate module/mapping manifest | all known fields disposed, private exclusions, source hashes | synthetic tests and private dry-run | product QA complete |
| S2 | generation writer, activation/archive/rollback | migration CLI, V4/V3 sync | pointer atomicity, rerun, crash recovery, current-history preservation | failure-path tests | product QA complete |
| S3 | coherent consumers and trends boundary | parser, calculator, proposals, core/docs | unified-only reads with legacy workspace compatibility | renderer/proposal/budget regressions | product QA complete |
| S4 | product QA and delivery | runners, workflow evidence, updater, private migration | no material findings, full checks, installed comparison, archive | validation records and private manifest | delivered; installed evidence recorded, formal final acceptance separate |

Stop rule: material unmapped value, ambiguous fact, source drift, privacy breach, dependency conflict or new scope blocks dependent activation; routine fixes inside this approved scope continue.

## Plan Quality Contract And DoD

DoD: every nonempty structured value accounted for; original Markdown hashes unchanged; one active coherent V4 generation; no active V3 dependency in migrated workspace; imported provenance and uncertainty preserved; no TaskNotes or other workspace mutations; verified rollback; current sync retains history. Artifact QA: architecture/plan/spec review before product writes. Implementation Quality Closure: Phase 5 findings-first whole-diff review, Phase 6 distillation, Phase 7 checkpoint. Required verification: aggregate runner, Personal Ops/V4, Weekly/V4, Task Management, SPOR, proposals, Dreaming, smoke, compile, diff check, full product and project Workflow validation. Quality-ready: no P0/P1/material P2 and complete evidence. Scripts are supporting-only. No deadline or timebox; no quality cutline. Model recommendation: frontier/workhorse high reasoning, non-blocking.

## Cutover And Rollback

Build candidate before replacing active data. Compare mapped values and unique sessions against frozen inputs. Verify installed product before local activation. Stage rollback copies of old official indexes and a journal before activation. Atomically select candidate, then archive prior active files. Interrupted archival resumes from journal. Rollback rebuilds compatible indexes from current canonical sources if new writes occurred; never restore stale counters. Generation validation detects corruption and source drift. No automatic fallback to mixed indexes after activation.

## Optional Knowledge Capture

Technical evidence, distillation and checkpoint required; no Codex memory writes.

## Owner Decision Checkpoint

Scope and high-risk approval explicit. Implementation and delivery approved; final Phase 8 not requested. Residual risk: legacy semantics may be incomparable; maintain original scale and confidence rather than infer.
