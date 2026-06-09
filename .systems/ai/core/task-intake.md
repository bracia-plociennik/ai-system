# Task Intake

## Purpose

Task intake is the mandatory pre-routing lens for new work in AI System.

It is not a phase and does not grant write permission. It decides whether the request is clear, safe, complete, and ready for planning or implementation.

## When To Use

Use task intake before:

- creating a client or project workspace;
- triaging a material dump request;
- planning or implementing new work;
- accepting a change request;
- creating a side task or micro-project;
- capturing memory when scope or privacy is unclear;
- proposing `system-insights`;
- automating or batching local file work.

If the owner asks only for status or command output, use guide or normal command routing.

## Required Summary

Use these sections:

### Co zostaje

What is clear, useful, safe, and should remain in scope.

### Co jest słabe / do poprawy lub usunięcia

What is vague, unsafe, over-scoped, duplicated, stale, or should be changed.

### Czego brakuje

Missing acceptance criteria, target workspace, ownership, privacy review, safe commands, required evidence, or owner approval.

### Blokery / decyzje

Blockers and decisions that prevent safe planning, writing, movement, distillation, or PASS.

### Rekomendowany routing

Choose one safe route:

- guide/status recovery;
- dump triage proposal;
- client workspace creation;
- project workspace creation;
- memory capture;
- distillation;
- system-insights anonymization proposal;
- change request;
- side task or micro-project;
- STOP for missing approval, ambiguous ownership, privacy risk, or unsafe external effects.

## Stop Conditions

Stop before planning or implementation when:

- the owner, client, project, or target path is ambiguous;
- acceptance criteria are missing and cannot be inferred safely;
- material may contain secrets, legal content, private customer data, or production data;
- real external effects are possible;
- requested writes lack `owner-approved`;
- the request would bypass validation, evidence, privacy, or stop conditions.

## Artifact Rules

Task intake may live in the response or in the artifact already being created.

Do not create a separate task-intake artifact unless the routed work already needs one.

Never store private client details in `.systems/`.
