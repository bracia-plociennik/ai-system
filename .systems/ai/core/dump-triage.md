# Dump Triage

## Purpose

`dump/` is the owner-controlled inbox for unclassified files.

## Flow

1. Owner places files in `ai-system-workspace/dump/incoming/`.
2. AI creates a classification proposal.
3. AI lists recommended target, confidence, risk, and reason.
4. Owner approves with `owner-approved`.
5. Only after approval may AI move, copy, link, rename, or archive files.

## Required Classification Fields

- source path;
- detected type;
- likely client;
- likely project;
- proposed target;
- confidence;
- privacy risk;
- required owner action.

## Stop Conditions

Stop when the file may contain credentials, legal content, private customer material, ambiguous ownership, or a destructive operation would be needed.
