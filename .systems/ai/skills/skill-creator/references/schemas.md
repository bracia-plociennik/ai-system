# Skill Creator Schemas

Use these schemas for local skill eval artifacts. Store runtime eval artifacts under an active project, micro-project, approved workspace path, or `/tmp`; do not store them under `.systems/ai/skills/**`.

## `evals.json`

```json
{
  "skill_name": "example-skill",
  "target_path": ".systems/ai/skills/example-skill",
  "mode": "manual-review",
  "created_for": "system-maintenance",
  "configurations": ["with_skill", "baseline"],
  "evals": [
    {
      "id": "eval-001",
      "name": "validation-evidence",
      "prompt": "Create a skill and show validation evidence.",
      "files": [],
      "expected_output": "A skill contract with local validation evidence.",
      "expected_behavior": [
        "Uses SKILL.md as canonical contract",
        "Keeps context source material out of active guidance",
        "Preserves authority boundaries",
        "Defines local validation"
      ],
      "forbidden_behavior": [
        "Writes runtime eval output into the skill directory",
        "Uses network resources without approval"
      ],
      "assertions": [
        {
          "text": "The output includes validation evidence",
          "type": "required",
          "method": "manual-review"
        }
      ]
    }
  ]
}
```

## `eval_metadata.json`

Located at `<run-dir>/<eval-id>/eval_metadata.json`.

```json
{
  "eval_id": "eval-001",
  "eval_name": "validation-evidence",
  "run_fingerprint": "<copy exact run.json fingerprint>",
  "metadata_fingerprint": "<copy exact matching metadata fingerprint>",
  "prompt": "Create a skill and show validation evidence.",
  "assertions": [
    {
      "text": "The output includes validation evidence",
      "type": "required",
      "method": "manual-review"
    }
  ],
  "configurations": ["with_skill", "baseline"]
}
```

## `run.json`

Located at `<run-dir>/run.json`.

```json
{
  "source_plan": "/tmp/evals.json",
  "skill_name": "example-skill",
  "target_path": ".systems/ai/skills/example-skill",
  "mode": "manual-review",
  "configurations": ["with_skill", "baseline"],
  "created_at": "2026-06-15T10:30:00Z",
  "eval_count": 1
}
```

## `metrics.json`

Located at `<run-dir>/<eval-id>/<configuration>/outputs/metrics.json` when available.

```json
{
  "tool_calls": {
    "read": 5,
    "edit": 2,
    "shell": 4
  },
  "total_tool_calls": 11,
  "total_steps": 5,
  "files_created": ["SKILL.md"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

## `timing.json`

Located at `<run-dir>/<eval-id>/<configuration>/timing.json` when available.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_duration_seconds": 18.0,
  "grader_duration_seconds": 5.3
}
```

## `grading.json`

Freshness contract 1 requires `eval_id`, `configuration`, `run_fingerprint` and
`metadata_fingerprint` in every grade. `run.json` binds the complete source plan,
configurations, membership, target skill files and explicit input fingerprints.
The producer checks existing grades before any overwrite; standalone aggregation repeats
the same checks. Historical unbound runs require a new run, not retroactive fingerprinting.

`result_fingerprints` binds the exact nonempty set of actual output/transcript files relative
to the configuration directory, excluding grading files and scaffold README/todo files.
Changing or adding an evaluated output invalidates the existing grade.

Located at `<run-dir>/<eval-id>/<configuration>/grading.json`.

```json
{
  "eval_id": "eval-001",
  "eval_name": "validation-evidence",
  "configuration": "with_skill",
  "skill_name": "example-skill",
  "mode": "manual-review",
  "score": 4,
  "passed": true,
  "reason": "The output met required expectations.",
  "expectations": [
    {
      "text": "The output includes validation evidence",
      "passed": true,
      "evidence": "review-notes.md lists the validator command output"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 0,
    "total": 1,
    "pass_rate": 1.0
  },
  "execution_metrics": {
    "total_tool_calls": 11,
    "errors_encountered": 0
  },
  "timing": {
    "total_tokens": 84852,
    "total_duration_seconds": 23.3
  },
  "claims": [
    {
      "claim": "All validators passed",
      "type": "quality",
      "verified": true,
      "evidence": "Attached validator output"
    }
  ],
  "user_notes_summary": {
    "uncertainties": [],
    "needs_review": [],
    "workarounds": []
  },
  "issues": [
    {
      "severity": "P3",
      "finding": "Assertion is broad",
      "fix": "Split validation evidence by command"
    }
  ],
  "eval_feedback": {
    "suggestions": [],
    "overall": "No suggestions"
  }
}
```

## `benchmark.json`

Located at `<run-dir>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "example-skill",
    "eval_count": 2,
    "configurations": ["with_skill", "baseline"]
  },
  "run_summary": {
    "with_skill": {
      "runs": 2,
      "pass_rate_mean": 1.0,
      "score_mean": 4.5,
      "time_seconds_mean": 22.0,
      "tokens_mean": 10000.0,
      "tool_calls_mean": 12.0,
      "errors_mean": 0.0
    },
    "baseline": {
      "runs": 2,
      "pass_rate_mean": 0.5,
      "score_mean": 3.0,
      "time_seconds_mean": 28.0,
      "tokens_mean": 12000.0,
      "tool_calls_mean": 16.0,
      "errors_mean": 1.0
    }
  },
  "deltas": {
    "with_skill_vs_baseline": {
      "pass_rate_delta": 0.5,
      "score_delta": 1.5,
      "time_seconds_delta": -6.0,
      "tokens_delta": -2000.0
    }
  },
  "runs": [
    {
      "eval_id": "eval-001",
      "configuration": "with_skill",
      "score": 4,
      "passed": true,
      "pass_rate": 1.0,
      "time_seconds": 23.3,
      "tokens": 84852,
      "tool_calls": 11,
      "errors": 0,
      "expectations": [
        {
          "text": "The output includes validation evidence",
          "passed": true,
          "evidence": "review-notes.md lists the validator command output"
        }
      ]
    }
  ],
  "blocking_findings": [
    {
      "eval_id": "eval-002",
      "configuration": "with_skill",
      "severity": "P2",
      "finding": "Skill output skipped required validation evidence"
    }
  ],
  "analyzer_notes": []
}
```

## `comparison.json`

Output from blind comparison.

```json
{
  "winner": "A",
  "confidence": "medium",
  "reasoning": "Output A is complete and validated.",
  "rubric": {
    "A": {
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content_score": 3.0,
      "structure_score": 3.0,
      "overall_score": 6.0
    }
  },
  "output_quality": {
    "A": {
      "strengths": ["Complete solution"],
      "weaknesses": []
    },
    "B": {
      "strengths": ["Readable"],
      "weaknesses": ["Missing validation"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 3,
      "total": 3,
      "pass_rate": 1.0
    },
    "B": {
      "passed": 2,
      "total": 3,
      "pass_rate": 0.67
    }
  }
}
```

## `analysis.json`

Output from post-hoc analysis.

```json
{
  "verdict": "needs-iteration",
  "main_failure_mode": "missing-validation",
  "configuration_result": {
    "with_skill_helped": "Higher pass rate on validation assertions",
    "with_skill_hurt": "No observed regression",
    "no_difference": "Both configurations produced similar README summaries"
  },
  "recommended_changes": [
    {
      "file": "SKILL.md",
      "change": "Add explicit validation evidence step",
      "reason": "Two evals skipped evidence"
    }
  ],
  "eval_design_changes": [
    "Add a separate assertion for each required validator command"
  ],
  "discarded_noise": [],
  "residual_risk": []
}
```

## `trigger-evals.json`

Use this for frontmatter description review.

```json
{
  "skill_name": "example-skill",
  "current_description": "Create example skills.",
  "queries": [
    {
      "id": "trigger-001",
      "query": "Create a new reusable AI System skill for frontend QA reviews",
      "should_trigger": true,
      "reason": "Direct skill creation request"
    },
    {
      "id": "trigger-002",
      "query": "Review this React component for accessibility",
      "should_trigger": false,
      "reason": "Needs a frontend review skill, not skill-creator"
    }
  ],
  "holdout_fraction": 0.4
}
```

## `description-optimization.json`

```json
{
  "skill_name": "example-skill",
  "candidate_description": "Create, update, and evaluate example skills...",
  "train_result": {
    "passed": 10,
    "total": 12
  },
  "holdout_result": {
    "passed": 5,
    "total": 8
  },
  "accepted": false,
  "reason": "Holdout misses adjacent negative cases"
}
```

## `feedback.json`

```json
{
  "status": "complete",
  "reviews": [
    {
      "run_id": "eval-001-with_skill",
      "feedback": "The output is correct but validation evidence is hard to scan.",
      "timestamp": "2026-06-15T10:30:00Z"
    }
  ]
}
```

## Field Rules

- `score`: number from 0 to 5.
- `passed`: boolean.
- `severity`: `P1`, `P2`, or `P3`.
- `mode`: `manual-review`, `local-script`, or `approved-subagent`.
- `configuration`: `with_skill`, `baseline`, `old_skill`, or another explicitly declared configuration.
- `evals[].id` and `configuration`: filesystem-safe names only; use letters, digits, dots, underscores, or hyphens and no path separators.
- `expected_behavior`: concrete outcomes, not broad preferences.
- `forbidden_behavior`: authority, safety, privacy, or scope violations.
- `expectations[].text`: original assertion text.
- `expectations[].passed`: boolean verdict.
- `expectations[].evidence`: specific evidence, not a generic statement.
